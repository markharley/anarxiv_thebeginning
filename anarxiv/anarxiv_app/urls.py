from django.conf.urls import url

from . import views

urlpatterns = [

	# Message submission and requests
	url(r'^result/messagesubmission/$', views.messageSubmission, name='messageSubmission'),

	url(r'^result/messagerequest/$', views.getMessages, name='getMessages'),

	# Search submissions, storage and requests
	url(r'^search/$', views.search, name='search'),


	# Links to single paper views
	url(r'^result/(?P<paperID>[a-zA-Z0-9._:-]+)/$', views.paperdisplay, name='paperdisplay'),

	# Subarxiv RSS rips and storage etc
	url(r'^subanarxiv/new/$', views.dailyPaperDisplay, name='subanarxiv_new'),

	# links to specific arxiv request
	url(r'^subanarxiv/search/$', views.specificRequest, name='specificRequest'),
	
	url(r'^subanarxiv/(?P<area>[a-zA-Z0-9._:-]+)/$', views.subanarxiv, name='subanarxiv'),


	# Login urls
	url(r'^register/check/email/', views.checkEmail , name='checkEmail'),
	url(r'^register/check/username/', views.checkUsername , name='checkUsername'),
	url(r'^register/registrationRequest', views.registrationRequest, name='registrationRequest'),
	url(r'^register/', views.registrationForm , name='registrationForm'),

	url(r'^login/', views.login, name='login'),

	url(r'^logout/', views.logout, name='logout'),

    url(r'^$', views.home, name='home'),
]