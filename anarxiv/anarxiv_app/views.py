from django.shortcuts import render_to_response
from django.http import HttpResponse
from anarxiv_app.models import paper

# Create your views here.


def home(request):
     return render_to_response('home.html')

def astrophysics(request):
     return render_to_response('astrophysics.html')

