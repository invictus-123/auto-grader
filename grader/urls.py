from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('signin', views.signin, name='signin'),
	path('signup', views.signup, name='signup'),
	path('signout', views.signout, name='signout'),
	url(r'^test/(?P<test_link>\w+)$', views.test_view, name='test'),
	url(r'^problem/(?P<problem_link>\w+)$', views.problem_view, name='problem'),
	url(r'^problem/(?P<problem_link>\w+)/submission$', views.submission, name='submission'),
	path('create-test', views.create_test, name='create-test'),
	url(r'^(?P<test_link>\w+)/create-problem$', views.create_problem, name='create-problem'),
]
