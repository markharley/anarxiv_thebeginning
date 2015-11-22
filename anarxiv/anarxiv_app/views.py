from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import Paper, Post
from django.template import Context, Template
import requests
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


def home(request):
     return render_to_response('home.html')

def subanarxiv(request,area):
	subAreas = {'astro':'Astrophysics', 'co-mp': 'Condensed Matter', 'gr-qc': 'General Relativity and Quantum Cosmology', 'hep-ex':'High Energy Physics - Experiment',
	'hep-ph':'High Energy Physics - Phenomenology','hep-th':'High Energy Physics-Theory', 'math-ph': 'Mathematical Phyiscs', 'nlin':'Nonlinear Sciences', 
	'nucl-ex':'Nuclear Experiment','nucl-th':'Nuclear Theory','physics':'Physics','quant-ph':'Quantum Physics'}
	context = {"SECTION": subAreas[area]}
	return render_to_response('subanarxiv.html', context)
	

@csrf_exempt
def search(request):
	surname = request.POST['info'] 
	
	baseurl = "https://inspirehep.net/"
   	url = baseurl + "search?ln=en&p=find+a+" + surname + "&of=recjson&action_search=Search&sf=earliestdate&so=d&rg=25&ot=recid,number_of_citations,authors,title,abstract"
   	r = requests.get(url)
   

   	template = loader.get_template("result_instance.html")


   	renderList = []

   	for article in r.json():
   		paper = {}
   		paper['title'] = article['title']['title']
   		paper['recid'] = article['recid']
   	
   		# The arXiv stores more than one abstract so this is the only way I can access it. Should be robust.
   		if isinstance(article['abstract'], list):
   			paper['abstract'] = article['abstract'][1]['summary']
   		else:
   			paper['abstract'] = article['abstract']['summary']

   		length = len(article['authors'])

   		Authors = ""
   		
   		for j in range(length):
   			Authors += (article['authors'][j]['first_name']) + " " +(article['authors'][j]['last_name']) 
   			if j==length-1:
   				Authors += '.'
   			else:
   				Authors += ', '	


		paper['authors'] = Authors
		paper['no_citations'] = article['number_of_citations']

		# Checks if the paper has already been added, only adds if it has not. Labeled by unique record id
		num = Paper.objects.filter(recordID = paper['recid']).count()
		if num == 0:
			paperObj = Paper(author = Authors, title=paper['title'], abstract = paper['abstract'],recordID = paper['recid'])
			paperObj.save()
		
				
		
		renderList.append(str(template.render(paper).encode('utf8')))

   	
   	return JsonResponse({'htmlList': renderList})


def paperdisplay(request, paperID):
	paperChoice = Paper.objects.get(recordID = str(paperID))

	
	context = {'title':paperChoice.title,'authors':paperChoice.author, 'paperID': paperChoice.recordID , 'abstract': paperChoice.abstract}


	url = "https://inspirehep.net/"+paperID +"/"
	return render_to_response('paper.html', context)





# This returns a JSON of the current message and appends it to the Paper object
@csrf_exempt
def messageSubmission(request):
	message = request.POST['message']     
	message_id = request.POST['id']

	# Create post object
	post = Post(paperID = message_id, message = message)
	post.save()

	context = {'message': message}
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
		context = {'message': comment.message}
		renderList.append(str(template.render(context).encode('utf8')))
		

	return JsonResponse({'messageHTML': renderList})









 