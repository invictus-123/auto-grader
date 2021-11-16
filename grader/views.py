from django.shortcuts import render
from grader.forms import UserForm, UserRoleForm, StudentDetailsForm
from django.contrib.auth.models import User
from grader.models import UserRole, StudentDetail, Test, Problem
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def index(request):
	context = {
		'title': 'Home'
	}
	if request.user.username:
		username = request.user.username
		role = UserRole.objects.get(user = request.user).role
		context['role'] = role

		if role == 'teacher':
			tests = request.user.test_set.all().filter(has_expired = False).order_by('-start_time')
			context['tests'] = tests

	return render(request, 'grader/index.html', context=context)

def signin(request):

	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username = username, password = password)

		print('hi')
		if user:
			print(username,password)
			if user.is_active:
				print(username,password)
				login(request, user)
				return HttpResponseRedirect(reverse('index'))

	context = {
		'title': 'Sign In',
	}
	return render(request, 'grader/signin.html', context=context)

@login_required
def signout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def signup(request):

	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))

	if request.method == 'POST':
		user_form = UserForm(request.POST)
		role_form = UserRoleForm(request.POST)
		student_details_form = StudentDetailsForm(request.POST)

		if user_form.is_valid() and role_form.is_valid():

			user = user_form.save()
			user.set_password(user.password)
			user.save()

			role = role_form.save(commit = False)
			role.user = user
			role.save()

			if(role_form.cleaned_data['role'] == 'student') and student_details_form.is_valid():
				detail = student_details_form.save(commit = False)
				detail.user = user
				detail.save()

			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(username = username, password = password)

			if user:
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect(reverse('index'))

	else:
		user_form = UserForm()
		role_form = UserRoleForm()
		student_details_form = StudentDetailsForm()

	context = {
		'title': 'Sign Up',
		'user_form': user_form,
		'role_form': role_form,
		'details_form': student_details_form,
	}
	return render(request, 'grader/signup.html', context=context)

@login_required
def problem(request, problem_link):

	try:
		prob = Problem.objects.get(link = problem_link)
		context = {
			'title': 'Problem',
			'prob': prob,
			'sample_output': '9'
		}
	except:
		return HttpResponse('Problem not found')
	return render(request, 'grader/problem.html', context=context)
