from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('signin', views.signin, name='signin'),
	path('signup', views.signup, name='signup'),
	path('signout', views.signout, name='signout'),
	url(r'^problem/(?P<problem_link>\w+)$', views.problem, name='problem')
]
