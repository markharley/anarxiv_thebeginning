from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Paper, Post, Author
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









 