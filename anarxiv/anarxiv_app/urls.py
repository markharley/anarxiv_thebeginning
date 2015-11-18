from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^search/(?P<surname>\w{0,10})/$', views.search, name='search'),
	url(r'^subanarxiv/(?P<area>[a-zA-Z0-9._-]+)/$', views.subanarxiv, name='subanarxiv'),
    url(r'^$', views.home, name='home'),
]