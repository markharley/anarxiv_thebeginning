from django.shortcuts import render_to_response
from django.http import HttpResponse
from anarxiv_app.models import paper
from django.template import Context, Template
import urllib, ssl, requests

# Create your views here.


def home(request):
     return render_to_response('home.html')

def astrophysics(request):
	context = {"title": "Gravitino cosmology in supersymmetric warm inflation", "author":"Sam Bartrum", "journalref":"Phys.Rev. D86 (2012) 123525"}
	return render_to_response('astrophysics.html', context)
	

def search(request):
	SecondName = request.GET['q']
   	url = "https://inspirehep.net/search?ln=en&p=find+a+" + SecondName +"&of=recjson&action_search=Search&sf=earliestdate&so=d&ot=recid,number_of_citations,authors,title"
   	r = requests.get(url)
   	return render_to_response('results.html', {'query':r.json()} )

