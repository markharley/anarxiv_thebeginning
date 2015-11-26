from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Paper, Post
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt
from lxml import html
import requests, json, feedparser, re


# Create your views here.


def home(request):
     return render_to_response('home.html')

@csrf_exempt
def subanarxiv_new(request):

	sub_section = str(request.POST['sub_anarxiv'])
	url = "http://arxiv.org/rss/" + sub_section
	d = feedparser.parse(url)
	template = loader.get_template("new_result_instance.html")
	renderList =[]

	for paper in d['entries']:
		abstract = paper['summary'][3:-2]
		title = paper['title']
		
		authors_unparsed = paper['author']
		t = re.split(r'<|>',authors_unparsed)
		a = ""

		if len(t)> 23:
			authors = a + t[2] + " et al"
		else:
			for i in range(2,len(t),4):
				a+= t[i]+ ", "
			authors = a[:-2] + "."	


		context = {'title': title, 'abstract': abstract, 'authors': authors, 'arxiv_no' : '124214'}

		renderList.append(str(template.render(context).encode('utf8')))


	return JsonResponse({'htmlList': renderList})







def subanarxiv(request,area):
	subAreas = {'astro-ph':'Astrophysics', 'cond-mat': 'Condensed Matter', 'gr-qc': 'General Relativity and Quantum Cosmology', 'hep-ex':'High Energy Physics - Experiment',
	'hep-ph':'High Energy Physics - Phenomenology','hep-th':'High Energy Physics-Theory','hep-lat':'High Energy Physics - Lattice', 'math-ph': 'Mathematical Physics', 'nlin':'Nonlinear Sciences', 
	'nucl-ex':'Nuclear Experiment','nucl-th':'Nuclear Theory','physics':'Physics','quant-ph':'Quantum Physics'}
	context = {"SECTION": subAreas[str(area)], "ABREV": area}
	return render_to_response('subanarxiv.html', context)

# Creates a dictionary that can be rendered to HTML to display the search results
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
	
	num = Paper.objects.filter(recordID = paperID).count()

	# Checks if the paper has already been added, only adds if it has not. Labeled by unique record id
	if num == 0:
		url = "https://inspirehep.net/record/"+paperID+"?of=recjson&ot=recid,number_of_citations,authors,title,abstract"
		r = requests.get(url).json()[0]
		title = r['title']['title']	
		recordID = r['recid']

		# The format the abstracts come in is non standard, this seems to pick up the cases well enough....
		if 'abstract' in r:
			if isinstance(r['abstract'], list):
				abstract = r['abstract'][0]['summary']
			else:
				abstract = r['abstract']['summary']
		else:
			abstract = "No abstract"	


		length = len(r['authors'])

		Authors = ""
		
		# At the moment I am storing the authors as a string in the model - this is perhaps not ideal....
		for j in range(length):
			Authors += (r['authors'][j]['first_name']) + " " +(r['authors'][j]['last_name']) 
			if j==length-1:
				Authors += '.'
			else:
				Authors += ', '	

		authors = Authors

		paperObj = Paper(author = authors, title = title, abstract = abstract, recordID = recordID)
		paperObj.save()


# This creates the single paper page HTML
def paperdisplay(request, paperID):
	# We store the paper in the Model
	paperStore(paperID)

	paperChoice = Paper.objects.get(recordID = str(paperID))

	Authors = paperChoice.author.split(',')

	allAuthors =""

	length = len(Authors)
	

	for author in Authors:
		allAuthors += author
		if author != Authors[length-1]:
			allAuthors += ', '	
	
	if length > 5:		
		shortList = Authors[0] + " et al..."		
	else: 
		shortList = allAuthors	

	context = {'title':paperChoice.title,'authors':allAuthors, 'shortList': shortList, 'paperID': paperChoice.recordID , 'abstract': paperChoice.abstract}


	url = "https://inspirehep.net/"+paperID +"/"
	return render_to_response('paper.html', context)




# The submitted message gets added to the Post model and returns the HTML rendered message
@csrf_exempt
def messageSubmission(request):
	message = request.POST['message']     
	message_id = request.POST['id']

	# Create post object
	post = Post(paperID = message_id, message = message)
	post.save()

	context = {'message': message, 'time': post.date}
	template = loader.get_template("message.html")

	temp = str(template.render(context).encode('utf8'))

	return JsonResponse({'messageHTML': temp})



# This returns a JSON of all previous messages for the paper we are looking at
@csrf_exempt
def getMessages(request):
	message_id = request.POST['id']

	posts = Post.objects.filter(paperID = message_id)

	template = loader.get_template("message.html")
	renderList = []

	for comment in posts:
		context = {'message': comment.message, 'time': comment.date}
		renderList.append(str(template.render(context).encode('utf8')))
		

	return JsonResponse({'messageHTML': renderList})









 