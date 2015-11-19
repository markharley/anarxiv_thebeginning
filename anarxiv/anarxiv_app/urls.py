from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^result/messagesubmission/$', views.messageSubmission, name='messageSubmission'),

	url(r'^result/messagerequest/$', views.getMessages, name='getMessages'),

	url(r'^search/(?P<surname>\w{0,10})/$', views.search, name='search'),

	url(r'^subanarxiv/(?P<area>[a-zA-Z0-9._-]+)/$', views.subanarxiv, name='subanarxiv'),

	url(r'^result/(?P<paperID>[a-zA-Z0-9._-]+)/$', views.paperdisplay, name='paperdisplay'),

    url(r'^$', views.home, name='home'),
]