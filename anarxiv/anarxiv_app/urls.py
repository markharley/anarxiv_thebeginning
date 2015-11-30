from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^result/messagesubmission/$', views.messageSubmission, name='messageSubmission'),

	url(r'^result/messagerequest/$', views.getMessages, name='getMessages'),

	url(r'^search/$', views.search, name='search'),

	url(r'^subanarxiv/new/$', views.subanarxiv_new, name='subanarxiv_new'),

	url(r'^subanarxiv/(?P<area>[a-zA-Z0-9._-]+)/$', views.subanarxiv, name='subanarxiv'),

	url(r'^result/(?P<paperID>[a-zA-Z0-9._-]+)/$', views.paperdisplay, name='paperdisplay'),

	url(r'^login/', views.login, name='login'),

	url(r'^logout/', views.logout, name='logout'),

    url(r'^$', views.home, name='home'),
]