from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import paper
from django.template import Context, Template
import requests

# Create your views here.


def home(request):
     return render_to_response('home.html')

def subanarxiv(request,area):
	subAreas = {'astro':'Astrophysics', 'co-mp': 'Condensed Matter', 'gr-qc': 'General Relativity and Quantum Cosmology', 'hep-ex':'High Energy Physics - Experiment',
	'hep-ph':'High Energy Physics - Phenomenology','hep-th':'High Energy Physics-Theory', 'math-ph': 'Mathematical Phyiscs', 'nlin':'Nonlinear Sciences', 
	'nucl-ex':'Nuclear Experiment','nucl-th':'Nuclear Theory','physics':'Physics','quant-ph':'Quantum Physics'}
	context = {"SECTION": subAreas[area]}
	return render_to_response('subanarxiv.html', context)
	


def search(request, surname):
	
	baseurl = "https://inspirehep.net/"
   	url = baseurl + "search?ln=en&p=find+a+" + surname + "&of=recjson&action_search=Search&sf=earliestdate&so=d&ot=recid,number_of_citations,authors,title,abstract"
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

		
		renderList.append(str(template.render(paper).encode('utf8')))

   	
   	return JsonResponse({'htmlList': renderList})

def paperdisplay(request, paperID):
	url = "https://inspirehep.net/"+paperID +"/"
	context = {'paperID': paperID, 'title': 'baladas', 'authors':'asdasd', 'journal_ref': 'asdas'}
	return render_to_response('paper.html', context)















 