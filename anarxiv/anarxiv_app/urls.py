from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^search/(?P<surname>\w{0,10})/$', views.search, name='search'),
	url(r'^astrophysics/$', views.astrophysics, name='astrophysics'),
    url(r'^$', views.home, name='home'),
]