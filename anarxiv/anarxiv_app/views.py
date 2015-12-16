from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Paper, Post, Author, newPaper, subArxiv
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt
from lxml import html
import requests, json, feedparser, re, urllib2, xmltodict, datetime
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


subAnarxivDictionary = {'physics:astro-ph':'Astrophysics', 'physics:cond-mat': 'Condensed Matter', 'physics:gr-qc': 'General Relativity and Quantum Cosmology', 'physics:hep-ex':'High Energy Physics - Experiment',
'physics:hep-ph':'High Energy Physics - Phenomenology','physics:hep-th':'High Energy Physics-Theory','physics:hep-lat':'High Energy Physics - Lattice', 'physics:math-ph': 'Mathematical Physics', 'physics:nlin':'Nonlinear Sciences', 
'physics:nucl-ex':'Nuclear Experiment','physics:nucl-th':'Nuclear Theory','physics:physics':'Physics','physics:quant-ph':'Quantum Physics',
'math':'Maths', 'cs':'Computer Science', 'stat':'Statistics', 'q-bio':'Quantative Biology', 'q-fin':'Quantative Finance'}


def home(request):
     return render(request,'home.html',{'subAnarxivs':subAnarxivDictionary})

def registrationForm(request):
	return render(request,'registration.html',{})

def login(request):
	try:
		attemptedUsername = request.POST['user']
		attemptedPassword = request.POST['password']
	except:
		return JsonResponse({'loginError' : 'true'})

	user = authenticate(username=attemptedUsername, password=attemptedPassword)

	if user is not None:
		auth_login(request,user)
		return JsonResponse({'username' : user.username})
	else:
		return JsonResponse({'loginError' : 'true'})

def logout(request):
	try:
		result=auth_logout(request)
	except:
		return JsonResponse({})
	return JsonResponse({"success" : "true"})

########################################################################################################################################################################################################

# SUBARXIV VIEWS

########################################################################################################################################################################################################


# Renders the subanarxiv page and send to client
def subanarxiv(request,area):
	thisDay = datetime.date.today()
	one_day = datetime.timedelta(days=1)
	FiveDays = [str(thisDay - x*one_day) for x in range(5)]
	context = {"SECTION": subAnarxivDictionary[str(area)], "ABREV": area, "DATE": FiveDays}
	return render(request,'subanarxiv.html', context)

# Gets last five days papers from the arxiv runs from command line "python manage.py getNewPapers"
def getDailyPapers():
	NoDays = 5
	thisDay = datetime.date.today()
	oneDay = datetime.timedelta(days=1)
	date = thisDay - oneDay*NoDays

	# requesting and accessing paper data

	url = 'http://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&from=' + str(date)

	urlfile = urllib2.urlopen(url)
	data = urlfile.read()
	urlfile.close()
	data = xmltodict.parse(data)
	papers = data['OAI-PMH']['ListRecords']['record']

	# Iterating over the papers 
	for paper in papers:

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
		date_added =  paper['header']['datestamp']

		title = article['title']
		abstract = article['abstract']
		arxiv_no = article['id']


		# Adding the paper to the temperary model only adds the paper if is not already in the database
		if newPaper.objects.filter(arxiv_no = arxiv_no).count() == 0:
			tempPap = newPaper(title = title, abstract = abstract, arxiv_no = arxiv_no, added_at = date_added)
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
			
			secondName = author['keyname']

			if Author.objects.filter(firstName = firstName, secondName = secondName).count() == 0:
		
				temp = Author(firstName = firstName, secondName = secondName)
				temp.save()
				# Adds the paper to the Author
				temp.newarticles.add(tempPap)
			
			else:
				temp = Author.objects.get(firstName = firstName, secondName = secondName)
				temp.newarticles.add(tempPap)	
		
# This takes the recently added papers out of the newPaper table and returns a rendered html response			
@csrf_exempt
def dailyPaperDisplay(request):
	sub_section = str(request.POST['sub_anarxiv'])
	date = request.POST['date']
	area = subArxiv.objects.get(region = sub_section)

	papers = area.newpaper_set.all().filter(added_at = date)

	template = loader.get_template("new_result_instance.html")
	renderList =[]

	for paper in papers:
		AuthorList = paper.author_set.all()
		allAuthors =""

		for author in AuthorList:

			allAuthors += author.firstName + " " + author.secondName + ", "
			
		allAuthors = allAuthors[:-2] + "."     # Sticks a full stop on the end because pretty
			
		# Prints "et al" for large numbers of authors
		if len(AuthorList) > 5:		
			shortList = AuthorList[0].firstName + " " + AuthorList[0].secondName + " et al..."	
			allAuthors = shortList	
	
		else: 
			shortList = allAuthors	

				

		context = {'title': paper.title, 'abstract': paper.abstract, 'shortList': shortList, 'authors': allAuthors, 'arxiv_no' : paper.arxiv_no, 'subanarxiv':subanarxiv}

		renderList.append(str(template.render(context).encode('utf8')))	


	return JsonResponse({'htmlList': renderList})

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
	renderList = []

	# Iterating over the papers 
	for paper in papers:

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

		AuthorList = ""	

		for author in newAuthors:
			if 'forenames' in author:
				firstName = author['forenames']
				AuthorList += firstName + " "
			
			secondName = author['keyname']
			AuthorList += secondName + ", "

		context = {'title': title, 'arxiv_no': arxiv_no}	

		renderList.append(str(template.render(context).encode('utf8')))		

	return JsonResponse({'htmlList': renderList})		
		

########################################################################################################################################################################################################

# SEARCH AND DISPLAY VIEWS

########################################################################################################################################################################################################


# Manipulates the json returned from Inspires into a form we can display (SINGLE PAPER)
def paperSearchDisplay(article):
	paper = {}
	paper['title'] = article['title']['title']
	paper['recid'] = article['recid']

	# The arXiv stores more than one abstract so this is the only way I can access it. Should be robust.
	if 'abstract' in article:
		if isinstance(article['abstract'], list):
			paper['abstract'] = article['abstract'][1]['summary']
		else:
			paper['abstract'] = article['abstract']['summary']
	else:
		paper['abstract'] = "No abstract"		


	# Gets the journal information
	info = article['publication_info']	
	journal_ref = info['title'] + info['volume'] +" " + "(" +info['year'] + ")" +" " + info['pagination'] + "."
	paper['journal_ref'] = journal_ref


	length = len(article['authors'])

	Authors = ""
	

	for j in range(length):
		Authors += (article['authors'][j]['first_name']) + " " +(article['authors'][j]['last_name']) 
		if length > 5:
			Authors += ' et al.'
			break
		if j==length-1:
			Authors += '.'
		else:
			Authors += ', '	

	
	paper['authors'] = Authors
	paper['no_citations'] = article['number_of_citations']		

	return paper	

# Returns JSON which is rendered for the search undertaken
@csrf_exempt
def search(request):
	surname = request.POST['info'] 
	
	baseurl = "https://inspirehep.net/"

	url = baseurl + "search?ln=en&ln=en&p=" + surname + "&of=recjson&action_search=Search&sf=earliestdate&so=d&rg=17&sc=0"
	r = requests.get(url)

	template = loader.get_template("result_instance.html")


	renderList = []

	for article in r.json():
		paper = paperSearchDisplay(article)
		
		renderList.append(str(template.render(paper).encode('utf8')))

	
	return JsonResponse({'htmlList': renderList})

# This function takes the paperID, performs the search and stores the paper in the Model.
def paperStore(paperID):
	
	url = "https://inspirehep.net/record/"+paperID+"?of=recjson&ot=recid,number_of_citations,authors,title,abstract,publication_info"
	r = requests.get(url).json()[0]
	title = r['title']['title']	
	Inspires_no = r['recid']

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
	journal_ref = info['title'] + info['volume'] +" " + "(" +info['year'] + ")" +" " + info['pagination'] + "."

	# Save the paper to the database
	paperObj = Paper(title = title, abstract = abstract, Inspires_no = Inspires_no, journal = journal_ref)
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
				
# This creates the single paper page for both arxiv and inspires papers
def paperdisplay(request, paperID):

	if paperID[0:6]=="arxiv:":
		paperChoice = newPaper.objects.get(arxiv_no = paperID[6:])
	else:
		# We store the paper in the Model if it is not already in the model
		num = Paper.objects.filter(Inspires_no = paperID).count()
	
		if num == 0:
			paperStore(paperID)

		paperChoice = Paper.objects.get(Inspires_no = paperID)

	# Returns set of authors related to this paper
	AuthorList = paperChoice.author_set.all()

	allAuthors =""

	for author in AuthorList:
		allAuthors += author.firstName + " " + author.secondName + ", "
	allAuthors = allAuthors[:-2] + "."     # Sticks a full stop on the end because pretty
	
	# Prints "et al" for large numbers of authors
	if len(AuthorList) > 5:		
		shortList = AuthorList[0].firstName + " " + AuthorList[0].secondName + " et al..."		
	
	else: 
		shortList = allAuthors	

	context = {'title': paperChoice.title, 'authors':allAuthors, 'shortList': shortList, 'paperID': paperChoice.Inspires_no , 'abstract': paperChoice.abstract, 'journal_ref':paperChoice.journal}

	return render_to_response('paper.html', context)


########################################################################################################################################################################################################

# MESSAGE SUBMISSION AND RETRIEVING VIEWS

########################################################################################################################################################################################################


# The submitted message gets added to the Post model and returns the HTML rendered message
@csrf_exempt
def messageSubmission(request):
	message = request.POST['message']     
	message_id = request.POST['id']

	paper = Paper.objects.get(Inspires_no = message_id)

	# Create post object
	post = Post(message = message, paper = paper)
	post.save()

	context = {'message': post.message, 'time': post.date}
	template = loader.get_template("message.html")

	temp = str(template.render(context).encode('utf8'))

	return JsonResponse({'messageHTML': temp})

# This returns a JSON of all previous messages for the paper we are looking at
@csrf_exempt
def getMessages(request):
	message_id = request.POST['id']

	paper = Paper.objects.get(Inspires_no = message_id)

	posts = paper.post_set.all()

	template = loader.get_template("message.html")
	renderList = []

	for comment in posts:
		context = {'message': comment.message, 'time': comment.date}
		renderList.append(str(template.render(context).encode('utf8')))
		

	return JsonResponse({'messageHTML': renderList})









 















