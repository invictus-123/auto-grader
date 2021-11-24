from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('signin', views.signin, name='signin'),
	path('signup', views.signup, name='signup'),
	path('signout', views.signout, name='signout'),
	path('create-test', views.create_test, name='create-test'),
	url(r'^test/(?P<test_link>\w+)$', views.test_view, name='test'),
	url(r'^test/(?P<test_link>\w+)/edit$', views.edit_test, name='edit-test'),
	url(r'^test/(?P<test_link>\w+)/delete$', views.delete_test, name='delete-test'),
	url(r'^test/(?P<test_link>\w+)/result$', views.result, name='result'),
	url(r'^test/(?P<test_link>\w+)/create-problem$', views.create_problem, name='create-problem'),
	url(r'^problem/(?P<problem_link>\w+)$', views.problem_view, name='problem'),
	url(r'^problem/(?P<problem_link>\w+)/delete$', views.delete_problem, name='delete-problem'),
	url(r'^problem/(?P<problem_link>\w+)/edit$', views.edit_problem, name='edit-problem'),
	url(r'^problem/(?P<problem_link>\w+)/submission$', views.submission, name='submission'),
]
