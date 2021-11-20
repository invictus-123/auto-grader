from django.shortcuts import render
from grader.forms import UserForm, UserRoleForm, StudentDetailsForm
from grader.judge import execute
from django.contrib.auth.models import User
from grader.models import UserRole, StudentDetail, Test, Problem, Submission
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import hashlib, random, datetime, pytz

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
			context['is_teacher'] = True
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
		username = request.user.username
		role = UserRole.objects.get(user = request.user).role
		is_teacher = True if role == 'teacher' else False
		context = {
			'title': 'Test - ' + test.title,
			'is_teacher': is_teacher,
			'test_link': test_link,
			'problems': problems
		}
		return render(request, 'grader/test.html', context=context)
	except:
		return HttpResponse('Test not found')

@login_required
def problem_view(request, problem_link):

	try:
		problem = Problem.objects.get(link = problem_link)
		sample_output = execute(problem.data['solution'], 'cpp', problem.data['sample_input'])
		context = {
			'title': 'Problem - ' + problem.title,
			'problem': problem,
			'test_link': problem.test.link,
			'sample_output': sample_output
		}

		if request.method == 'POST':
			user_code = request.POST.get('code')
			author_code = problem.data['solution']
			cnt = 0
			for test in problem.data['tests']:
				user_output = execute(user_code, 'cpp', test)
				author_output = execute(author_code, 'cpp', test)
				if author_output == user_output:
					cnt += 1
				else:
					break
			score = problem.data['marks'] if cnt == len(problem.data['tests']) else 0

			print(request.user,problem)

			submission = Submission(
				user = request.user,
				problem = problem,
				solution = user_code,
				score = score
			)
			print('here')
			submission.save()

			return HttpResponse('submitted')
			# return render(request, 'grader/submission.html')

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

	if request.method == 'POST':
		title = request.POST.get('title')
		semester = request.POST.get('semester')
		branch = request.POST.get('branch')
		duration = int(request.POST.get('duration'))
		start_time = pytz.utc.localize(datetime.datetime.strptime(request.POST.get('starttime'), '%Y-%m-%dT%H:%M'))
		link = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

		if timezone.now() < start_time:
			has_expired = False
		else:
			delta = timezone.now() - start_time
			has_expired = True if delta.total_seconds() / 60 >= duration else False

		test = Test(
			user = request.user,
			title = title,
			link = link,
			semester = semester,
			branch = branch,
			duration = duration,
			start_time = start_time,
			has_expired = has_expired
		)

		test.save()

		return HttpResponseRedirect(reverse('index'))

	context = {
		'title': 'Create Test',
	}
	return render(request, 'grader/create_test.html', context=context)

@login_required
def create_problem(request, test_link):

	role = UserRole.objects.get(user = request.user).role
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	if request.method == 'POST':
		test = Test.objects.get(link = test_link)

		title = request.POST.get('title')
		statement = request.POST.get('statement')
		problem_type = request.POST.get('type')
		test_cases = request.POST.getlist('test-case')
		sample_input = request.POST.get('sample-input')
		link = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
		solution = request.POST.get('code')
		marks = int(request.POST.get('marks'))

		prob = Problem(
			test = test,
			title = title,
			type = problem_type,
			link = link,
			data = {
				'statement': statement,
				'sample_input': sample_input,
				'tests': test_cases,
				'solution': solution,
				'marks': marks
			}
		)
		prob.save()

		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	context = {
		'title': 'Create Problem',
		'test_link': test_link,
	}
	return render(request, 'grader/create_problem.html', context=context)
