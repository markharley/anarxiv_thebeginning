from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Comment, Paper, Post, Author, newPaper, subArxiv, User, ActivationRequest
from django.template import Context, Template, RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from lxml import html
import requests, json, feedparser, re, urllib2, xmltodict, datetime, time, urllib, calendar
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from collections import defaultdict
import string
import uuid
from django.core.mail import send_mail
from django.shortcuts import redirect

# To be extensible shall we dump this dictionary in the DB?
subAnarxivDictionary = {'physics:astro-ph':'Astrophysics', 'physics:cond-mat': 'Condensed Matter', 'physics:gr-qc': 'General Relativity and Quantum Cosmology', 'physics:hep-ex':'High Energy Physics - Experiment',
'physics:hep-ph':'High Energy Physics - Phenomenology','physics:hep-th':'High Energy Physics-Theory','physics:hep-lat':'High Energy Physics - Lattice', 'physics:math-ph': 'Mathematical Physics', 'physics:nlin':'Nonlinear Sciences',
'physics:nucl-ex':'Nuclear Experiment','physics:nucl-th':'Nuclear Theory','physics:physics':'Physics','physics:quant-ph':'Quantum Physics',
'math':'Maths', 'cs':'Computer Science', 'stat':'Statistics', 'q-bio':'Quantative Biology', 'q-fin':'Quantative Finance'}

def home       (request): return render(request, 'home.html')
def searchpage (request): return render(request, 'searchpage.html')
def profilepage(request): return render(request, 'profilepage.html')

########################################################################################################################################################################################################

# Log in and regestration views

########################################################################################################################################################################################################

def registrationForm(request):
	return render(request,'registration.html',{})

def checkEmail(request):
	try:
		attemptedEmail=request.POST["email"]
	except:
		return JsonResponse({})

	if User.objects.filter(email=attemptedEmail).exists():
		return JsonResponse({"emailAvailable" : "inUse"})
	else:
		return JsonResponse({"emailAvailable" : "available"})

def checkUsername(request):
	try:
		attemptedUsername=request.POST["username"]
	except:
		return JsonResponse({})

	if User.objects.filter(username=attemptedUsername).exists():
		return JsonResponse({"usernameAvailable" : "inUse"})
	else:
		return JsonResponse({"usernameAvailable" : "available"})

def registrationRequest(request):

	# Get the information from post
	try:
		email=request.POST["email"]
		username=request.POST["username"]
		password=request.POST["password"]
		academicQ=(request.POST["academicQ"]=="true")

	# If this fails then return fail to JS
	except:
		return JsonResponse({'error': 'Useful message for the front-end here'})

	# Try to make the new user model
	try:
		newUser = User.objects.create_user(email,username,password,academicQ)
		newUser.save()

	# If this fails then return fail to JS
	except:
		return JsonResponse({'error': 'Useful message for the front-end here'})

	# Generate a hash
	registerHash = uuid.uuid4().hex

	# Make the account request
	ActivationRequest(user=newUser, registerHash=registerHash).save()

	# Send an activation email to the new users email address
	body = 'click here to confirm your account\n\nhttp://127.0.0.1:8000/home/activation/' + \
		str(registerHash) + '\n\nCheers,\nAnarix Admin.'

	try:
		send_mail('Your Anarxiv account has been created!', body, 'admin@anarxiv.co.uk', [newUser.email])

	# This will fail if we're running locally so just print out the email instead...
	except:
		print '\n\n\nSending:\n', body, '\n to', newUser.email

	# Otherwise return success!
	return JsonResponse({'success': 'Welcome to Anarxiv!  Please confirm your account via email'})

# Users get here by following a link in an email which has a unique hash
def activate(request, registerHash):

	# Get the activation request from the hash
	activationRequest = ActivationRequest.objects.filter(registerHash=registerHash)

	# If we returned more than one freak the fuck out
	if len(activationRequest) > 1:
		print '?!'
		return

	# Else we're ok...
	else:
		activationRequest = activationRequest[0]

	# Activate the user form the request
	activationRequest.user.isActive = True
	activationRequest.user.save()

	# Delete this request
	activationRequest.delete()

	# Bounce the user to the login page
	return redirect('/home/')

# Request a password reset
def resetRequest(request):

	# Get the email
	email = request.POST.get('email', None)

	# Check we have that user's email
	try:
		user = User.objects.get(email=email)
	except:
		return JsonResponse({'error': 'Sorry We don\'t have an account registered with that email address.'})

	# Generate a new password
	newPassword = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(30))
	user.set_password(newPassword)
	user.save()

	# Send an email to the user
	body = 'Hello,\n\nYour new password is ' + newPassword + '\n\nThis is a temporary password and will expire in one hour.' + \
	       'Pleasse login and change it at www.anarxiv.co.uk\n\nThanks!\n\nAnarxiv Admin'

	# Make sure te password will expire
	user.passwordExpiry = datetime.now() + D(hours=1)
	user.save()

	# if we're on the server
	try:
		send_mail('Anarxiv password reset request', body, 'admin@anarxiv.co.uk', [user.email], fail_silently=False)
	except:
		print '\nEMAIL SENT:\nfrom: admin@anarxiv.co.uk\nto:' + str(user.email) + '\nAccount Verification\n' + body + '\n '

	# Send the user to 'login'
	return JsonResponse({'success': 'We have sent a password reset email to your email account'})

def login(request):

	try:
		attemptedUsername = request.POST['user']
		attemptedPassword = request.POST['password']
	except:
		return JsonResponse({'loginError' : 'true'})

	# Returns a User if the username and password match
	user = authenticate(username=attemptedUsername, password=attemptedPassword)

	# Debugging...
	# for user in User.objects.all(): print user.email

	# Did we find a user with those details?
	if user is not None:

		# Is the user active?
		if user.isActive:

			# Check to see if the user is using a temporary password
			if user.passwordExpiry:

				if user.passwordExpiry < datetime.now():

					return JsonResponse({'error': "Your temporary password has expired please use the 'forgotten password' " +\
					                      "form to get a new password (and remember to change it within an hour!)"})
			else:
				auth_login(request,user)
				print "{'username' : user.username}"
				return JsonResponse({'username' : user.username})
		else:

			print "{'error': 'Activate your account first'}"
			return JsonResponse({'error': 'Activate your account first'})
	else:
		print "{'error': 'Email or password incorrect'}"
		return JsonResponse({'error': 'Email or password incorrect'})

def logout(request):
	try:
		result=auth_logout(request)
	except:
		return JsonResponse({})
	return JsonResponse({"success" : "true"})

########################################################################################################################################################################################################

# MASS PAPER STORAGE - these dont seem to be views really, they might want to be in a different module?

########################################################################################################################################################################################################

# Stores the new papers in the newPaper model
def newPaperStore(paper):
	# This creates the subarxiv areas
	sub = paper['header']['setSpec']
	if isinstance(sub,list) == False:
		subareas = []
		subareas.append(sub)
	else:
		subareas = sub

	for subarea in subareas:
		if subArxiv.objects.filter(region = subarea).count() == 0:
			subarx = subArxiv(region = subarea)
			subarx.save()


	article = paper['metadata']['arXiv']

	# Checks if the paper is new or has been updated (if it's been updated it is not new)
	if 'updated' in article:
		newtemp = 'no'
	else:
		newtemp = 'yes'


	date_added =  paper['header']['datestamp']
	title = article['title']
	abstract = article['abstract']
	arxiv_no = article['id']


	# Adding the paper to the temperary model only adds the paper if is not already in the database
	if newPaper.objects.filter(arxiv_no = arxiv_no).count() == 0:
		tempPap = newPaper(title = title, abstract = abstract, arxiv_no = arxiv_no, added_at = date_added, new = newtemp)
		tempPap.save()
		# Attaches the subarxivs to the paper
		for subarea in subareas:
			temp = subArxiv.objects.get(region = subarea)
			tempPap.area.add(temp)

	else:
		tempPap = newPaper.objects.get(arxiv_no = arxiv_no)
		for subarea in subareas:
			temp = subArxiv.objects.get(region = subarea)
			tempPap.area.add(temp)


	# Attaches the authors to the paper
	authors = article['authors']['author']

	if isinstance(authors,list) == False:
		newAuthors = []
		newAuthors.append(authors)
	else:
		newAuthors = authors


	for author in newAuthors:
		if 'forenames' in author:
			firstName = author['forenames']
		else:
			firstName = None

		secondName = author['keyname']

		if Author.objects.filter(firstName = firstName, secondName = secondName).count() == 0:

			temp = Author(firstName = firstName, secondName = secondName)
			temp.save()
			# Adds the paper to the Author
			temp.newarticles.add(tempPap)

		else:
			temp = Author.objects.get(firstName = firstName, secondName = secondName)
			temp.newarticles.add(tempPap)

# Gets last five days papers from the arxiv runs from command line "python manage.py getNewPapers"
def getDailyPapers():
	NoDays = 5
	thisDay = datetime.date.today()
	oneDay = datetime.timedelta(days=1)
	date = thisDay - oneDay*NoDays

	# requesting and accessing paper data
	baseurl = 'http://export.arxiv.org/oai2?verb=ListRecords'
	url = baseurl + '&metadataPrefix=arXiv&from=' + str(date)

	while True:

		try:
			urlfile = urllib2.urlopen(url)

		# if this request fails we wait for 30s before rerequesting
		except urllib2.HTTPError, e:
			if e.code == 503:
				to = int(e.hdrs.get("retry-after", 30))

				time.sleep(to)
				continue

			else:
				raise


		data = urlfile.read()
		urlfile.close()
		data = xmltodict.parse(data)
		papers = data['OAI-PMH']['ListRecords']['record']

		# Iterating over the papers
		for paper in papers:
			newPaperStore(paper)

		# Gets the resumptionToken if it exists and adjusts the url accordingly
		if 'resumptionToken' in data['OAI-PMH']['ListRecords'] and '#text' in data['OAI-PMH']['ListRecords']['resumptionToken']:
			resumptionToken = data['OAI-PMH']['ListRecords']['resumptionToken']['#text']
			url = baseurl + '&resumptionToken=' + resumptionToken

		else:
			break

# This function takes the paperID, performs the search and stores the paper in the Model
def paperStore(paperID, api):

	if api == "Inspires":
		url = "https://inspirehep.net/record/"+str(paperID)+"?of=recjson&ot=recid,number_of_citations,authors,title,abstract,publication_info,primary_report_number"

	elif api == "arXiv":
		url = "https://inspirehep.net/search?ln=en&p="+str(paperID)+"&of=recjson&ot=recid,number_of_citations,authors,title,abstract,publication_info,primary_report_number"

	r = requests.get(url).json()[0]
	title = r['title']['title']
	Inspires_no = r['recid']

	if isinstance(r['primary_report_number'],list):
		arxiv_no = r['primary_report_number'][0]
	else:
		arxiv_no = r['primary_report_number']

	# The format the abstracts come in is non standard, this seems to pick up the cases well enough....
	if 'abstract' in r:
		if isinstance(r['abstract'], list):
			abstract = r['abstract'][0]['summary']
		else:
			abstract = r['abstract']['summary']
	else:
		abstract = "No abstract"

	# Create the journal ref
	info = r['publication_info']
	if info != None:
		journal_ref = info['title'] + info['volume'] +" " + "(" +info['year'] + ")" +" " + info['pagination'] + "."
	else:
		journal_ref = None

	# Save the paper to the database
	paperObj = Paper(title = title, abstract = abstract, Inspires_no = Inspires_no, journal = journal_ref, arxiv_no = arxiv_no)
	paperObj.save()

	# Adds the authors to the database ad links them to the paper
	length = len(r['authors'])

	for i in range(length):
		PaperObj = Paper.objects.get(Inspires_no = Inspires_no)

		# Checks to see if the Author is already in the database (use unique id in future)
		if Author.objects.filter(firstName = r['authors'][i]['first_name'], secondName = r['authors'][i]['last_name']).count() == 0:

			temp = Author(firstName = r['authors'][i]['first_name'], secondName = r['authors'][i]['last_name'] )
			temp.save()
			temp.articles.add(PaperObj)

		# Adds the paper to the Author
		else:
			temp = Author.objects.get(firstName = r['authors'][i]['first_name'], secondName = r['authors'][i]['last_name'])
			temp.articles.add(PaperObj)

	return paperObj

def updatePapers():
	NoDays = 4
	thisDay = datetime.date.today()
	oneDay = datetime.timedelta(days=1)
	date = thisDay - oneDay*NoDays

	papers = newPaper.objects.filter(added_at = date)

	for article in papers:
		posts = article.post_set.all()
		# Deletes the paper if it has not comments on it
		if len(posts) == 0:
			article.delete()
		else:
			url = "https://inspirehep.net/search?of=recjson&ln=en&ln=en&p=find+eprint+arxiv:"+ str(article.arxiv_no) + "&of=hb&action_search=Search&sf=earliestdate&so=d&rm=&rg=25&sc=0"
			try:
				data = requests.get(url).json()
				inspires_no = data[0]['recid']
				paperStore(inspires_no)

				# Move the messages over
				y = Paper.objects.get(Inspires_no = inspires_no)
				posts = article.post_set.all()
				for post in posts:
					temp = post.message
					temp2 = Post(message = temp, paper = y)
					temp2.save()

				# Delete the paper
				article.delete()

			except ValueError:
				pass

# This takes the recently added papers out of the newPaper table and returns a rendered html response
@csrf_exempt
def dailyPaperDisplay(request):
	sub_section = str(request.POST['sub_anarxiv'])
	date = request.POST['date']
	area = subArxiv.objects.get(region = sub_section)

	papers = area.newpaper_set.all().filter(added_at = date)

	template = loader.get_template("result_instance.html")
	newList =[]
	replacementList = []
	newindex = 1
	replacementindex = 1

	for paper in papers:
		AuthorList = paper.author_set.all()

		if paper.new =='no':
			index = replacementindex
			replacementindex+=1

		else:
			index = newindex
			newindex+=1


		context = {'title': paper.title, 'abstract': paper.abstract, 'recid' : paper.arxiv_no, 'subanarxiv':subanarxiv,
					'arxiv_no': paper.arxiv_no, 'new': paper.new, 'authorlist':AuthorList, 'arxivlink': "http://arxiv.org/abs/" + paper.arxiv_no, 'resultnumber':index}

		# We add the paper to the replacement list if it has been updated, if it has not then it is new.
		if paper.new == 'no':
			replacementList.append(str(template.render(context).encode('utf8')))

		else:
			newList.append(str(template.render(context).encode('utf8')))


	return JsonResponse({'newList': newList, 'replacementList': replacementList})

# This is a specific search function for the arxiv takes a specific date and area as the input
@csrf_exempt
def specificRequest(request):
	date = request.POST['date']
	area = request.POST['sub_anarxiv']
	startDate = datetime.datetime.strptime(date, "%Y-%m-%d")

	url = 'http://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&set=' + area + '&from=' + str(startDate) + '&until=' + str(startDate)


	urlfile = urllib2.urlopen(url)
	data = urlfile.read()
	urlfile.close()
	data = xmltodict.parse(data)
	papers = data['OAI-PMH']['ListRecords']['record']

	template = loader.get_template("result_instance.html")

	newList = []
	replacementList = []
	newindex = 1
	replacementindex = 1


	# Iterating over the papers
	for paper in papers:
		AuthorList = []

		article = paper['metadata']['arXiv']
		date_added =  paper['header']['datestamp']

		title = article['title']
		abstract = article['abstract']
		arxiv_no = article['id']

		authors = article['authors']['author']

		if isinstance(authors,list) == False:
			newAuthors = []
			newAuthors.append(authors)
		else:
			newAuthors = authors


		for author in newAuthors:
			name = {'firstName':"", 'secondName': ""}

			if 'forenames' in author:
				name['firstName'] = author['forenames']

			name['secondName'] = author['keyname']
			AuthorList.append(name)


		if 'updated' in article:
			index = replacementindex
			replacementindex+=1

		else:
			index = newindex
			newindex+=1


		context = {'title': title, 'authorlist': AuthorList, 'arxiv_no': arxiv_no, 'resultnumber':index}

		# We add the paper to the replacement list if it has been updated, if it has not then it is new.
		if 'updated' in article:
			replacementList.append(str(template.render(context).encode('utf8')))
		else:
			newList.append(str(template.render(context).encode('utf8')))


	return JsonResponse({'newList': newList, 'replacementList':replacementList})


# Renders the subanarxiv page and send to client
def subanarxiv(request,area):
	thisDay = datetime.date.today()
	one_day = datetime.timedelta(days=1)
	Days = []

	for x in range(5):
		Day = {'DayName': calendar.day_name[(thisDay - x*one_day).weekday()], 'Date': str(thisDay - x*one_day) }
		Days.append(Day)


	context = {"SECTION": subAnarxivDictionary[str(area)], "ABREV": area, 'Dates': Days}
	return render(request,'subanarxiv.html', context)

########################################################################################################################################################################################################

# SEARCH VIEWS

########################################################################################################################################################################################################

# creates a dictionary for a single paper from the Inspires search
def inspiresDisplay(article):
	paper = defaultdict(lambda: None)
	paper['title'] = article['title']['title']
	paper['inspiresnumber'] = article['recid']
	paper['inspireslink'] = "http://inspirehep.net/record/" + str(article['recid'])

	if 'url' in article:
		if isinstance(article['url'], list):
			paper['pdflink'] = article['url'][0]['url']
		else:
			paper['pdflink'] = article['url']['url']

	# Finding the arXiv number associated with the paper
	if 'primary_report_number' in article:
		if not isinstance(article['primary_report_number'],list):
			if article['primary_report_number'][0:5] == "arXiv":
				paper['arxiv_no'] = article['primary_report_number'][6:]
			else:
				paper['arxiv_no'] = article['primary_report_number'].replace("/","+")

		else:
			for entry in article['primary_report_number']:
				if entry[0:5] == "arXiv":
					paper['arxiv_no'] = entry[6:]




	if paper['arxiv_no']!= None and '-' in paper['arxiv_no']:
		paper['arxivlink'] = "http://arxiv.org/abs/" + paper['arxiv_no']
	elif paper['arxiv_no']!= None:
		paper['arxivlink'] = "http://arxiv.org/abs/" + paper['arxiv_no']

	# The arXiv stores more than one abstract so this is the only way I can access it. Should be robust.
	if 'abstract' in article:
		if isinstance(article['abstract'], list):
			paper['abstract'] = article['abstract'][1]['summary']
		else:
			paper['abstract'] = article['abstract']['summary']
	else:
		paper['abstract'] = "No abstract"

	# Gets the journal information
	if 'publication_info' in article:
		info = article['publication_info']
		if 'title' in info:
			journal_ref = info['title']
			if 'volume' in info and 'pagination' in info:
				journal_ref += info['volume'] +" " + "(" +info['year'] + ")" +" " + info['pagination'] + "."

			paper['journal_ref'] = journal_ref
		else:
			paper['journal_ref'] = "No publication data."
	else:
		paper['journal_ref'] = "No publication data."



	AuthorList= []

	for author in  article['authors']:
		temp = {'firstName': author['first_name'], 'secondName': author['last_name']}
		AuthorList.append(temp)


	paper['authorlist'] = AuthorList
	paper['no_citations'] = "Citations: " + str(article['number_of_citations'])

	return paper


# This performs a quick xml request to calculate the total number of results generated in an inspires search.
def findResultsNumber(searchdata):
	urlconverted = urllib.quote_plus(searchdata)
	url = "https://inspirehep.net/search?p=" + urlconverted + "&of=xm&ot=100,245"
	urlfile = urllib2.urlopen(url)
	data = urlfile.read()
	A = data.split(" ")
	for x in A:
	    if x == 'Search-Engine-Total-Number-Of-Results:':
	    	numResults =  A[A.index(x)+1]

	return numResults


# Inspires search returns a list of papers
def InspiresSearch(searchdata, searchtype, start):

	baseurl = "https://inspirehep.net/"

	if start != "":
		startrecord = "&jrec=" + str(start)

	else:
		startrecord = ""

	if searchtype == "general":
		url = baseurl + "search?ln=en&ln=en&p=" + searchdata + "&of=recjson&action_search=Search&sf=earliestdate&so=d&rg=50&sc=0" + startrecord

	elif searchtype == "specific":
		url = baseurl +"record/" + searchdata + "?of=recjson&"

	try:
		r = requests.get(url)
		papers = r.json()

	except:
		return []

	paperList = []

	for article in papers:
		paperList.append(inspiresDisplay(article))

	return paperList

# Creates a dictionary for a single paper from an arXiv search
def arxivDisplay(article):
	paper = defaultdict(lambda: None)
	paper['title'] = article['title']

	temp = article['id'].split("abs/")[-1]

	if '/' in temp:
		temp = temp.replace('/','+')

	if 'v' in temp:
		temp = temp.split('v')[0]

	paper['arxiv_no'] = temp

	paper['arxivlink'] = article['id']

	if 'summary' in article:
		paper['abstract'] = article['summary']

	# Gets the journal information

	if 'arxiv:journal_ref' in article:
		paper['journal_ref'] = article['arxiv:journal_ref']['#text']

	else:
		paper['journal_ref'] = "No publication data."


	# in the case of a single author we need to insert it into a list to then manipulate
	if isinstance(article['author'],list) == False:
		authorlist= []
		authorlist.append(article['author'])
	else:
		authorlist = article['author']

	AuthorList =[]

	for author in authorlist:
		firstName = author['name'].split(" ")[0]
		secondName = " ".join(author['name'].split(" ")[1:])
		authordict = {'firstName': firstName, 'secondName': secondName}
		AuthorList.append(authordict)

	paper['authorlist'] = AuthorList

	return paper


# arXiv search returns a list of papers
def arXivSearch(searchdata,start):

	searchdata = searchdata.replace(" ","+AND+")

	if start != "":
		initresult = "&start="+ str(start)
	else:
		initresult = ""

	baseurl = "http://export.arxiv.org/api/"
	url = baseurl + "query?search_query=all:" + searchdata + initresult+"&max_results=50&sortBy=lastUpdatedDate&sortOrder=descending"
	urlfile = urllib2.urlopen(url)
	data = urlfile.read()
	urlfile.close()
	data = xmltodict.parse(data)

	# this is the list of papers
	if 'entry' in data['feed']:
		papers = data['feed']['entry']
		totalResults = data['feed']['opensearch:totalResults']['#text']
		startIndex = data['feed']['opensearch:startIndex']['#text']

		if isinstance(papers,list) == False:
			articles = []
			articles.append(papers)
		else:
			articles = papers


		template = loader.get_template("result_instance.html")

		paperList = []

		for article in articles:
			paperList.append(arxivDisplay(article))


		return {'totalResults':totalResults, 'startIndex': startIndex, 'paperList': paperList}

	else:
		return {}

# Combines the results of the two searches which will catch the edge cases which don't appear in both the arXiv and Inspires
def InsparXivSearch(searchdata, searchtype, start):
	A = arXivSearch(searchdata,start)['paperList']
	I = InspiresSearch(searchdata, searchtype, start)

	numArXiv = arXivSearch(searchdata,start)['totalResults']
	numInspires = findResultsNumber(searchdata)

	# Creates a list of arxiv_numbers to allow for easier comparison
	arXivnums = [x['arxiv_no'] for x in I]
	titles = [x['title'] for x in I]
	ReducedList = []

	# Creates a new list of inspires results which aren't already in the arXiv results
	for x in A:
		if x['arxiv_no'] not in arXivnums:
			if x['title'] not in titles:
				ReducedList.append(x)

	return I + ReducedList

# Search engine
@csrf_exempt
def search(request):
	searchinfo = request.POST['info']
	selectedsearch = request.POST['search']
	template = loader.get_template("result_instance.html")
	renderList = []

	start = int(request.POST['index'])*50



	if selectedsearch == "Inspires":
		# convert the string into a url friendly form
		urlconverted = urllib.quote_plus(searchinfo)
		# returns the number of results
		numResults = findResultsNumber(searchinfo)

		paperList = InspiresSearch(urlconverted, "general", start)

		for paper in paperList:
			paper['resultnumber'] = str(paperList.index(paper)+ start + 1)
			renderList.append(str(template.render(paper).encode('utf8')))

		return JsonResponse({'htmlList': renderList, 'totalResults':numResults, 'startIndex': start})

	if selectedsearch == "arXiv":
		temp = arXivSearch(searchinfo, start)
		paperList = temp['paperList']
		numResults = temp['totalResults']
		startIndex = temp['startIndex']

		for paper in paperList:
			paper['resultnumber'] = str(paperList.index(paper)+start+1)
			renderList.append(str(template.render(paper).encode('utf8')))

		return JsonResponse({'htmlList': renderList, 'totalResults':numResults, 'startIndex': startIndex})


	if selectedsearch == "InsparXiv":
		paperList = InsparXivSearch(searchinfo, "general",start)

		for paper in paperList:
			paper['resultnumber'] = str(paperList.index(paper)+start+1)
			renderList.append(str(template.render(paper).encode('utf8')))

		return JsonResponse({'htmlList': renderList, 'totalResults':numResults, 'startIndex': start})

########################################################################################################################################################################################################

# DISPLAY VIEWS

########################################################################################################################################################################################################

# This creates the single paper page for both arxiv and inspires papers
def paperdisplay(request, paperID):

	# It it has an arxiv prefix we search the newPaper and Paper models for it
	if paperID[0:6]=="arXiv:":

		if '+' in paperID:
			paperID = paperID.replace('+','/')

		# This cuts off the version modification to the end of the arXiv number
		if "v" in paperID[6:]:
			temp = paperID[6:].split("v")[0]

		else:
			temp = paperID[6:]

		# if the paper is in newPaper
		if newPaper.objects.filter(arxiv_no = temp).count() != 0:
			paperChoice = newPaper.objects.get(arxiv_no = temp)

		# if the paper is in Paper
		elif Paper.objects.filter(arxiv_no = temp).count() !=0:
			paperChoice = Paper.objects.get(arxiv_no = temp)

		# otherwise we request the info from the arXiv API
		else:
			paper = arXivSearch(temp,"")['paperList'][0]
			paperChoice = "NONE"


	# in this case the paper if is an inspires number
	else:
		# if the paper is in newPaper
		if newPaper.objects.filter(Inspires_no = paperID).count() != 0:
			paperChoice = newPaper.objects.get(Inspires_no = paperID)

		# if the paper is in Paper
		elif Paper.objects.filter(Inspires_no = paperID).count() !=0:
			paperChoice = Paper.objects.get(Inspires_no = paperID)

		else:
			paper = InspiresSearch(paperID, "specific","")[0]
			paperChoice = "NONE"


	# If the paper was already stored we render it as follows
	if paperChoice != "NONE":
		# Returns set of authors related to this paper
		temp = paperChoice.author_set.all()
		AuthorList= []
		for x in temp:
			temp2 = {'firstName':x.firstName, 'secondName':x.secondName}
			AuthorList.append(temp2)

		temp = "http://arxiv.org/pdf/" + str(paperChoice.arxiv_no) + ".pdf"

		context = {'title': paperChoice.title, 'authorlist': AuthorList,  'paperID': paperChoice.Inspires_no , 'abstract': paperChoice.abstract,
					'journal_ref':paperChoice.journal, 'arxivno':paperChoice.arxiv_no, 'pdflink': temp}

	else:
		if paper['arxiv_no'] != None:
			if '+' in paper['arxiv_no']:
				paper['arxiv_no'] = paper['arxiv_no'].replace("+","/")
			temp = "http://arxiv.org/pdf/" + paper['arxiv_no'] + ".pdf"
		elif paper['pdflink'] != None:
			temp = paper['pdflink']
		else:
			temp = "NOLINK"

		context = {'title': paper['title'], 'paperID': paper['inspiresnumber'] , 'abstract': paper['abstract'],
					'journal_ref':paper['journal_ref'],'arxivno': paper['arxiv_no'], 'pdflink':temp, 'authorlist': paper['authorlist']}

	return render(request,'paper.html', context)

########################################################################################################################################################################################################

# MESSAGE SUBMISSION AND RETRIEVING VIEWS

########################################################################################################################################################################################################

# The submitted message gets added to the Post model and returns the HTML rendered message
@csrf_exempt
def messageSubmission(request):
	message = request.POST['message']
	message_id = request.POST['id']
	arxivno = request.POST['arxivno']

	# Check if the message is clean or not
	if not checkClean(message):
		return JsonResponse({'messageHTML': 'UNCLEAN'})

	else:

		# If the paper has an arXiv number
		if arxivno != '0':

			# We check the newPaper and Paper databases
			if newPaper.objects.filter(arxiv_no = arxivno).count() != 0:
				paper = newPaper.objects.get(arxiv_no = arxivno)
				numposts = len(paper.post_set.all())
				post = Post(message = message, new_paper = paper, messageID = numposts+1, poster = request.user)

			elif Paper.objects.filter(arxiv_no = arxivno).count() != 0:
				paper = Paper.objects.get(arxiv_no = arxivno)
				numposts = len(paper.post_set.all())
				post = Post(message = message, paper = paper, messageID = numposts+1, poster = request.user)

			# Else we create the paper object
			else:
				p = arXivSearch(arxivno,"")['paperList'][0]
				paper = Paper(title=p['title'], abstract= p['abstract'], arxiv_no= p['arxiv_no'], journal = p['journal_ref'])
				paper.save()
				post = Post(message = message, paper = paper, messageID = 1, poster = request.user)

				authors = p['authorlist']

				for author in authors:

					if Author.objects.filter(firstName = author['firstName'], secondName = author['secondName']).count() == 0:

						temp = Author(firstName = author['firstName'], secondName = author['secondName'])
						temp.save()
						# Adds the paper to the Author
						temp.articles.add(paper)

					else:
						temp = Author.objects.get(firstName = author['firstName'], secondName = author['secondName'])
						temp.articles.add(paper)





		# If the paper does not have an arXiv number
		else:
			# We just have to look for the paper in the Paper database
			if Paper.objects.filter(Inspires_no = message_id).count() == 1:
				paper = Paper.objects.get(Inspires_no = message_id)
				numposts = len(paper.post_set.all())
				post = Post(message = message, paper = paper, messageID = numposts + 1, poster = request.user)

			# Else we create the paper object
			else:
				temp = paperStore(message_id, "Inspires")
				post = Post(message = message, paper = temp, messageID = 1, poster = request.user)


		post.save()


		context = {'message': post.message, 'time': post.date, 'number': post.messageID, 'user': post.poster.username}
		template = loader.get_template("message.html")

		temp = str(template.render(context).encode('utf8'))

		return JsonResponse({'messageHTML': temp, 'message_number':post.messageID})

# This returns a JSON of all rendered previous messages for the paper we are looking at
@csrf_exempt
def getMessages(request):
	message_id = request.POST['id']
	arxiv_no = request.POST['arxivno']
	renderList = []
	template = loader.get_template("message.html")
	commenttemplate = loader.get_template("comment.html")

	# If the paper has an arXiv number we search for it in the databases
	if arxiv_no != '0':

		if newPaper.objects.filter(arxiv_no = arxiv_no).count() == 1:
			article = newPaper.objects.get(arxiv_no = arxiv_no)

		elif Paper.objects.filter(arxiv_no = arxiv_no).count() == 1:
			article = Paper.objects.get(arxiv_no = arxiv_no)

		else:
			article = "NONE"

	# If the paper has an Inspires number but no arXiv number so we only check the Paper database
	else:

		if Paper.objects.filter(Inspires_no = str(message_id)).count() ==1:
			article = Paper.objects.get(Inspires_no = str(message_id))
		else:
			article = "NONE"


	if article != "NONE":
		posts = article.post_set.all()


		for p in posts:
			commentList =[]
			subcomments = p.comment_set.all()

			for x in subcomments:
				context = {'message': x.comment, 'time': x.date, 'user': x.commenter.username}
				temp = str(commenttemplate.render(context).encode('utf8'))
				commentList.append(temp)

			context = {'message': p.message, 'time': p.date, 'number': p.messageID, 'user':p.poster, 'upvotes':p.upVotes}
			renderList.append( {'post': str(template.render(context).encode('utf8')),'comments':commentList, 'id': p.messageID} )



	return JsonResponse({'messageHTML': renderList})

def authorPage(request, authorID):
	firstName = authorID.split("+")[0]
	secondName = " ".join(authorID.split("+")[1:])

	if Author.objects.filter(firstName = firstName, secondName = secondName).count() != 0:
		author = Author.objects.get(firstName = firstName, secondName = secondName)

		papers = [x for x in author.articles.all()]
		newpapers = [x for x in author.newarticles.all()]
		totalPapers = papers + newpapers


		paperswithposts = []
		for paper in totalPapers:
			x = paper.post_set.all()
			if len(x) > 0:
				paperswithposts.append(paper)

	else:
		totalPapers = [{'title': 'NONE FOUND'}]
		paperswithposts=[{'title': 'NONE FOUND'}]




	context = {'author': firstName+" " +secondName, 'papers': totalPapers, 'paperswithposts': paperswithposts}

	return render_to_response('author.html', context)

@csrf_exempt
def commentSubmission(request):
	comment = request.POST['comment']
	messageid = request.POST['messageid']
	Inspiresno = request.POST['id']
	arxiv_no = request.POST['arxivno']

	if arxiv_no != '0':

		if newPaper.objects.filter(arxiv_no = arxiv_no).count() == 1:
			article = newPaper.objects.get(arxiv_no = arxiv_no)

		elif Paper.objects.filter(arxiv_no = arxiv_no).count() == 1:
			article = Paper.objects.get(arxiv_no = arxiv_no)

		else:
			article = "NONE"

	# If the paper has an Inspires number but no arXiv number so we only check the Paper database
	else:

		if Paper.objects.filter(Inspires_no = str(Inspiresno)).count() ==1:
			article = Paper.objects.get(Inspires_no = str(Inspiresno))
		else:
			article = "NONE"



	message = Post.objects.get(messageID = messageid, paper =article)

	newcomment = Comment(comment = comment, parentmessage = message, commenter = request.user)
	newcomment.save()

	numcomments = len(message.comment_set.all())


	context = {'message': newcomment.comment, 'time': newcomment.date, 'number': messageid, 'user':newcomment.commenter.username}
	template = loader.get_template("comment.html")

	temp = str(template.render(context).encode('utf8'))

	return JsonResponse({'messageHTML': temp, 'num_comments': numcomments})

# Maybe stick this in another file
def checkClean(stringwords):
	parseArray = (stringwords.lower()).split(" ")

	swearwords = ['fuck','shit','cunt','twat','penis','dick']

	for word in parseArray:
		if word in swearwords:
			return False


	return True

