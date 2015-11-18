from django.shortcuts import render_to_response, render, loader
from django.http import HttpResponse, JsonResponse
from anarxiv_app.models import paper
from django.template import Context, Template
import requests

# Create your views here.


def home(request):
     return render_to_response('home.html')

def astrophysics(request):
	context = {"title": "Gravitino cosmology in supersymmetric warm inflation", "author":"Sam Bartrum", "journalref":"Phys.Rev. D86 (2012) 123525"}
	return render_to_response('astrophysics.html', context)
	


def search(request, surname):
	
	baseurl = "https://inspirehep.net/"
   	url = baseurl + "search?ln=en&p=find+a+" + surname + "&of=recjson&action_search=Search&sf=earliestdate&so=d&ot=recid,number_of_citations,authors,title"
   	r = requests.get(url)
   	
   	template = loader.get_template("result_instance.html")


   	renderList = []
   	
   	for i in range(len(r.json())):
   		paper = {}
   		paper['title'] = r.json()[i]['title']['title']

   		length = len(r.json()[i]['authors'])

   		Authors = ""
   		for j in range(length):
   			Authors += (r.json()[i]['authors'][j]['first_name']) + " " +(r.json()[i]['authors'][j]['last_name']) 
   			if j==length-1:
   				Authors += '.'
   			else:
   				Authors += ', '	


		paper['authors'] = Authors
		paper['no_citations'] = r.json()[i]['number_of_citations']

		
		renderList.append(str(template.render(paper).encode('utf8')))

   	
   	return JsonResponse({'htmlList': renderList})



 