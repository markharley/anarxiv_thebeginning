from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^search/$', views.search, name='search'),
	url(r'^astrophysics/$', views.astrophysics, name='astrophysics'),
    url(r'^$', views.home, name='home'),
]