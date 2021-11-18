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
			tests = request.user.test_set.all().filter(has_expired = False).order_by('start_time')
			context['tests'] = tests
		else:
			details = StudentDetail.objects.get(user = request.user)
			tests = Test.objects.all().filter(has_expired = False, branch = details.branch, semester = details.semester).order_by('start_time')
			context['tests'] = tests

	return render(request, 'grader/index.html', context=context)

def signin(request):

	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username = username, password = password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))

	context = {
		'title': 'Sign In',
	}
	return render(request, 'grader/signin.html', context=context)

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
def signout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

@login_required
def test_view(request, test_link):

	try:
		test = Test.objects.get(link = test_link)
		problems = Problem.objects.all().filter(test = test)
		context = {
			'title': 'Test - ' + test.title,
			'problems': problems
		}
		return render(request, 'grader/test.html', context=context)
	except:
		return HttpResponse('Test not found')

@login_required
def problem_view(request, problem_link):

	try:
		prob = Problem.objects.get(link = problem_link)
		context = {
			'title': 'Problem - ' + prob.title,
			'prob': prob,
			'sample_output': '9'
		}
	except:
		return HttpResponse('Problem not found')
	return render(request, 'grader/problem.html', context=context)

@login_required
def submission(request, problem_link):
	return HttpResponse('Submission')

@login_required
def create_test(request):

	role = UserRole.objects.get(user = request.user).role
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	return HttpResponse('Working')

@login_required
def create_problem(request):

	role = UserRole.objects.get(user = request.user).role
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	context = {
		'title': 'Create Test',
	}
	return render(request, 'grader/create_problem.html', context=context)
