from django.shortcuts import render
# from django.http import HttpResponse
from models import Client

# Create your views here.

def getHome(request):

	return render(request, 'temp.html', {'text': 'HIYA'})

def makeClient(request):

	temp = Client(name="Test Client")
	temp.save()

	return render(request, 'temp.html', {'text': 'Made client'})

def getClient(request):

	temp = Client.objects.get(name="Test Client")

	return render(request, 'temp.html', {'text': temp.name})