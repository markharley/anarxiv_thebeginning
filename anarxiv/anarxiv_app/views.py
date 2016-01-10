from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Paper, Post, Author, newPaper, subArxiv
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt
from lxml import html
import requests, json, feedparser, re, urllib2, xmltodict, datetime, time, urllib
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from collections import defaultdict


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

# SUBARXIV VIEWS AND MASS PAPER STORAGE

########################################################################################################################################################################################################


# Renders the subanarxiv page and send to client
def subanarxiv(request,area):
	thisDay = datetime.date.today()
	one_day = datetime.timedelta(days=1)
	FiveDays = [str(thisDay - x*one_day) for x in range(5)]
	context = {"SECTION": subAnarxivDictionary[str(area)], "ABREV": area, "DATE": FiveDays}
	return render(request,'subanarxiv.html', context)

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

# def thisDaysPapers():
# 	NoDays = 0
# 	thisDay = datetime.date.today()
# 	oneDay = datetime.timedelta(days=1)
# 	date = thisDay - oneDay*NoDays

# 	# requesting and accessing paper data
# 	baseurl = 'http://export.arxiv.org/oai2?verb=ListRecords'
# 	url = baseurl + '&metadataPrefix=arXiv&from=' + str(date)

# 	while True:

# 		try: 
# 			urlfile = urllib2.urlopen(url)
		
# 		# if this request fails we wait for 30s before rerequesting
# 		except urllib2.HTTPError, e:
# 			if e.code == 503:
# 				to = int(e.hdrs.get("retry-after", 30))

# 				time.sleep(to)
# 				continue
			   
# 			else:
# 				raise		


# 		data = urlfile.read()
# 		urlfile.close()
# 		data = xmltodict.parse(data)
# 		papers = data['OAI-PMH']['ListRecords']['record']

# 		# Iterating over the papers 
# 		for paper in papers:
# 			newPaperStore(paper)

# 		# Gets the resumptionToken if it exists and adjusts the url accordingly	
# 		if 'resumptionToken' in data['OAI-PMH']['ListRecords'] and '#text' in data['OAI-PMH']['ListRecords']['resumptionToken']:
# 			resumptionToken = data['OAI-PMH']['ListRecords']['resumptionToken']['#text']
# 			url = baseurl + '&resumptionToken=' + resumptionToken 

# 		else:
# 			break	 

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

	for paper in papers:
		AuthorList = paper.author_set.all()
		allAuthors =""

		for author in AuthorList:
			if author.firstName != None:
				allAuthors += author.firstName + " " + author.secondName + ", "		
			else:
				allAuthors +=  author.secondName + ", "		
					
			
		allAuthors = allAuthors[:-2] + "."     # Sticks a full stop on the end because pretty
			
		# Prints "et al" for large numbers of authors
		if len(AuthorList) > 5:		
			if AuthorList[0].firstName != None:
				shortList = AuthorList[0].firstName + " " + AuthorList[0].secondName + " et al..."	
			else:
				shortList = AuthorList[0].secondName + " et al..."	

			allAuthors = shortList	
	
		else: 
			shortList = allAuthors	

		context = {'title': paper.title, 'abstract': paper.abstract, 'shortList': shortList, 'authors': allAuthors, 'recid' : 'arxiv:'+ paper.arxiv_no, 'subanarxiv':subanarxiv, 'arxiv_no': paper.arxiv_no, 'new': paper.new}
	
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
	renderList = []
	newList = []
	replacementList = []

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

		if 'forenames' in newAuthors[0]:	
			ShortList = newAuthors[0]['forenames'] + " " + newAuthors[0]['keyname'] + " et al.."	
		else:
			ShortList = newAuthors[0]['keyname'] + " et al.."			

		# Chose whether to use the short list of the long list	
		if len(newAuthors) >5:
			ListToUse = ShortList
		else:
			ListToUse = AuthorList	


		context = {'title': title, 'authors': ListToUse, 'arxiv_no': arxiv_no}	

		# We add the paper to the replacement list if it has been updated, if it has not then it is new.
		if 'updated' in article:
			replacementList.append(str(template.render(context).encode('utf8')))		
		else:
			newList.append(str(template.render(context).encode('utf8')))		
		

	return JsonResponse({'htmlList': renderList, 'newList': newList, 'replacementList':replacementList})		
		

########################################################################################################################################################################################################

# SEARCH VIEWS

########################################################################################################################################################################################################


# creates a dictionary for a single paper from the Inspires search
def inspiresDisplay(article):
	paper = defaultdict(lambda: None)
	paper['title'] = article['title']['title']
	paper['inspiresnumber'] = article['recid']
	paper['inspireslink'] = "http://inspirehep.net/record/" + str(article['recid'])

	# Finding the arXiv number associated with the paper
	if 'primary_report_number' in article:
		if not isinstance(article['primary_report_number'],list):
			paper['arxiv_no'] = article['primary_report_number']
		
		else:	
			for entry in article['primary_report_number']:
				if entry[0:5] == "arXiv":
					paper['arxiv_no'] = entry	

	
	if paper['arxiv_no']!= None and '-' in paper['arxiv_no']:	
		paper['arxivlink'] = "http://arxiv.org/abs/" + paper['arxiv_no']
	elif paper['arxiv_no']!= None:	
		paper['arxivlink'] = "http://arxiv.org/abs/" + paper['arxiv_no'][6:]	

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
			if 'volume' in info:
				journal_ref += info['volume'] +" " + "(" +info['year'] + ")" +" " + info['pagination'] + "."
			
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


# Inspires search returns a list of papers
def InspiresSearch(searchdata, searchtype):
	
	baseurl = "https://inspirehep.net/"

	if searchtype == "general":
		url = baseurl + "search?ln=en&ln=en&p=" + searchdata + "&of=recjson&action_search=Search&sf=earliestdate&so=d&rg=25&sc=0"
	
	elif searchtype == "specific":
		url = baseurl +"record/" + searchdata + "?of=recjson&ot=recid,number_of_citations,authors,title"
	
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

	temp = article['id'].split("/")[-1]
	if 'v' in temp:
		paper['arxiv_no'] =  "arXiv:" + temp.split('v')[0]


	paper['arxivlink'] = article['id']

	if 'summary' in article:
		paper['abstract'] = article['summary']

	# Gets the journal information

	if 'arxiv:journal_ref' in article:
		paper['journal_ref'] = article['arxiv:journal_ref']['#text']


	# in the case of a single author we need to insert it into a list to then manipulate	
	if isinstance(article['author'],list) == False:
		authorlist= []
		authorlist.append(article['author'])
	else:
		authorlist = article['author']

	length = len(authorlist)

	Authors = ""
	
	for j in range(length):
		Authors += (authorlist[j]['name']) + " "  
		if length > 5:
			Authors += ' et al.'
			break
		if j==length-1:
			Authors += '.'
		else:
			Authors += ', '	

	
	paper['authors'] = Authors	

	return paper	


# arXiv search returns a list of papers
def arXivSearch(searchdata):

	searchdata = searchdata.replace(" ","+AND+")

	baseurl = "http://export.arxiv.org/api/" 
	url = baseurl + "query?search_query=all:" + searchdata + "&start=0&max_results=50&sortBy=lastUpdatedDate&sortOrder=descending"
	urlfile = urllib2.urlopen(url)
	data = urlfile.read()
	urlfile.close()
	data = xmltodict.parse(data)

	# this is the list of papers
	if 'entry' in data['feed']:
		papers = data['feed']['entry']
		totalResults = data['feed']['opensearch:totalResults']
		
		if isinstance(papers,list) == False:
			articles = []
			articles.append(papers)
		else:
			articles = papers


		template = loader.get_template("result_instance.html")

		paperList = []

		for article in articles:
			paperList.append(arxivDisplay(article))


		return paperList	
		
	else:
		return []	

# Combines the results of the two searches which will catch the edge cases which don't appear in both the arXiv and Inspires
def InsparXivSearch(searchdata, searchtype):
	A = arXivSearch(searchdata)
	I = InspiresSearch(searchdata, searchtype)

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
	

	if selectedsearch == "Inspires":
		# convert the string into a url friendly form
		urlconverted = urllib.quote_plus(searchinfo)
		
		paperList = InspiresSearch(urlconverted, "general")

		for paper in paperList:
			paper['resultnumber'] = str(paperList.index(paper)+1)
			renderList.append(str(template.render(paper).encode('utf8')))

		return JsonResponse({'htmlList': renderList})

	if selectedsearch == "arXiv":
		paperList = arXivSearch(searchinfo)	

		for paper in paperList:
			paper['resultnumber'] = str(paperList.index(paper)+1)
			renderList.append(str(template.render(paper).encode('utf8')))

		return JsonResponse({'htmlList': renderList})


	if selectedsearch == "InsparXiv":
		paperList = InsparXivSearch(searchinfo, "general")

		for paper in paperList:
			paper['resultnumber'] = str(paperList.index(paper)+1)
			renderList.append(str(template.render(paper).encode('utf8')))

		return JsonResponse({'htmlList': renderList})


########################################################################################################################################################################################################

# DISPLAY VIEWS

########################################################################################################################################################################################################



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
				
# This creates the single paper page for both arxiv and inspires papers
def paperdisplay(request, paperID):

	# It it has an arxiv prefix we search the newPaper and Paper models for it
	if paperID[0:6]=="arXiv:":

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
			paper = arXivSearch(temp)[0]
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
			paper = InspiresSearch(paperID, "specific")[0]	
			paperChoice = "NONE"



	# If the paper was already stored we render it as follows	
	if paperChoice != "NONE":	
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

		context = {'title': paperChoice.title, 'authors':allAuthors, 'shortList': shortList, 'paperID': paperChoice.Inspires_no , 'abstract': paperChoice.abstract, 'journal_ref':paperChoice.journal, 'arxivno':paperChoice.arxiv_no}

	else:
		context = {'title': paper['title'], 'authors':paper['authors'], 'paperID': paper['arxiv_no'] , 'abstract': paper['abstract'], 'journal_ref':paper['journal_ref']}	
	
	return render_to_response('paper.html', context)


########################################################################################################################################################################################################

# MESSAGE SUBMISSION AND RETRIEVING VIEWS

########################################################################################################################################################################################################


# The submitted message gets added to the Post model and returns the HTML rendered message
@csrf_exempt
def messageSubmission(request):
	message = request.POST['message']     
	message_id = request.POST['id']
	arxiv_no = request.POST['arxivno']

	# If the paper does not have an inspires id, then it is in the temperary db
	if message_id == '0':
		paper = newPaper.objects.get(arxiv_no = arxiv_no)
		post = Post(message = message, new_paper = paper)
	# Otherwise we look for it in the permanent db
	else:
		paper = Paper.objects.get(Inspires_no = message_id)
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
	arxiv_no = request.POST['arxivno']

	# If the paper does not have an inspires id, then it is in the temperary db
	if message_id == '0':
		article = newPaper.objects.get(arxiv_no = arxiv_no)
	# Otherwise we look for it in the permanent db
	else:
		article = Paper.objects.get(Inspires_no = str(message_id))

	posts = article.post_set.all()


	template = loader.get_template("message.html")
	renderList = []

	for comment in posts:
		context = {'message': comment.message, 'time': comment.date}
		renderList.append(str(template.render(context).encode('utf8')))
		

	return JsonResponse({'messageHTML': renderList})









 















