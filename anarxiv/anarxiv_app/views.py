from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Paper, Post, Author, newPaper
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt
from lxml import html
from datetime import datetime
import requests, json, feedparser, re


subAreas = {'astro-ph':'Astrophysics', 'cond-mat': 'Condensed Matter', 'gr-qc': 'General Relativity and Quantum Cosmology', 'hep-ex':'High Energy Physics - Experiment',
'hep-ph':'High Energy Physics - Phenomenology','hep-th':'High Energy Physics-Theory','hep-lat':'High Energy Physics - Lattice', 'math-ph': 'Mathematical Physics', 'nlin':'Nonlinear Sciences', 
'nucl-ex':'Nuclear Experiment','nucl-th':'Nuclear Theory','physics':'Physics','quant-ph':'Quantum Physics'}


def home(request):
	 return render_to_response('home.html')



########################################################################################################################################################################################################

# SUBARXIV VIEWS

########################################################################################################################################################################################################


# Renders the subanarxiv page and send to client
def subanarxiv(request,area):
	context = {"SECTION": subAreas[str(area)], "ABREV": area}
	return render_to_response('subanarxiv.html', context)

# Method to rip the papers off the RSS feeds and store in the newPaper table
def getDailyPapers(request):
	# Work out how to trigger this from a cron set up

	# This wipes the table
	newPaper.objects.all().delete()

	for sub_section in subAreas:
		url = "http://arxiv.org/rss/" + sub_section
		papers = feedparser.parse(url)['entries']
		
		for paper in papers:
			abstract = paper['summary'][3:-2]
			title = paper['title']
			arxiv_no = paper['id'].split("/")[-1]
			
			# Adding the paper to the temperary model
			tempPap = newPaper(title = title, abstract = abstract, subarxiv = sub_section, arxiv_no = arxiv_no)
			tempPap.save()	


			# Relating the paper to the relevant authors - NEED TO SORT OUT ASCII TO UTF8 ENCODING
			authors_unparsed = paper['author']
			t = re.split(r'<|>',authors_unparsed)

			for i in range(2,len(t),4):
				# Surname is the last element of the array
				secondName = t[i].split(" ")[-1]
				# First names are the rest of the array, this includes middle name abrevs
				firstName = " ".join(t[i].split(" ")[0:-1])

				if Author.objects.filter(firstName = firstName, secondName = secondName).count() == 0:
			
					temp = Author(firstName = firstName, secondName = secondName)
					temp.save()
					# Adds the paper to the Author
					temp.newarticles.add(tempPap)
				
				else:
					temp = Author.objects.get(firstName = firstName, secondName = secondName)
					temp.newarticles.add(tempPap)	

	# allows for a test				
	return render_to_response('home.html') 				


# This takes the recently added papers out of the newPaper table and returns a rendered html response			
@csrf_exempt
def dailyPaperDisplay(request):
	sub_section = str(request.POST['sub_anarxiv'])

	papers = newPaper.objects.filter(subarxiv = sub_section)

	template = loader.get_template("result_instance.html")
	renderList =[]

	for paper in papers:
		AuthorList = paper.author_set.all()

		for author in AuthorList:
			allAuthors =""

			allAuthors += author.firstName + " " + author.secondName + ", "
			allAuthors = allAuthors[:-2] + "."     # Sticks a full stop on the end because pretty
		
			# Prints "et al" for large numbers of authors
			if len(AuthorList) > 5:		
				shortList = AuthorList[0].firstName + " " + AuthorList[0].secondName + " et al..."		
		
			else: 
				shortList = allAuthors	

		context = {'title': paper.title, 'abstract': paper.abstract, 'shortList': shortList, 'authors': allAuthors, 'arxiv_no' : '124214'}

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

# Returns rendered json to the client which can be inserted dynamically (ALL SEARCH RESULTS)
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
	
				
# This creates the single paper page HTML
def paperdisplay(request, paperID):
	
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









 















