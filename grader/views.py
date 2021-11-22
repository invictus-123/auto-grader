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
from django.db.models import F
import hashlib, random, datetime, pytz

def index(request):
	context = {
		'title': 'Home'
	}
	if request.user.username:
		username = request.user.username
		role = UserRole.objects.get(user = request.user).role
		context['role'] = role

		cur_time = timezone.localtime(timezone.now())
		if role == 'teacher':
			tests = Test.objects.all().filter(user = request.user)
		else:
			details = StudentDetail.objects.get(user = request.user)
			tests = Test.objects.all().filter(branch = details.branch)
			tests = tests.filter(semester = details.semester)
			tests = tests.filter(end_time__gte = cur_time)
		context['is_teacher'] = True if role == 'teacher' else False
		tests = tests.order_by('start_time')
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
		role = UserRole.objects.get(user = request.user).role
		cur_time = timezone.localtime(timezone.now())
		if test.end_time >= cur_time and role == 'student':
			return HttpResponseRedirect(reverse('test', args = (test_link,)))
		problems = Problem.objects.all().filter(test = test)
		username = request.user.username
		is_teacher = True if role == 'teacher' else False
		cur_time = timezone.localtime(timezone.now())
		has_ended = True if test.end_time < cur_time else False
		context = {
			'title': 'Test - ' + test.title,
			'is_teacher': is_teacher,
			'test_link': test_link,
			'has_ended': has_ended,
			'problems': problems
		}
		return render(request, 'grader/test.html', context=context)
	except:
		return HttpResponse('Test not found')

@login_required
def problem_view(request, problem_link):

	try:
		problem = Problem.objects.get(link = problem_link)
		sample_output = execute(problem.data['solution'], 'c', problem.data['sample_input'])
		context = {
			'title': 'Problem - ' + problem.title,
			'problem': problem,
			'test_link': problem.test.link,
			'sample_output': sample_output
		}

		if request.method == 'POST':
			role = UserRole.objects.get(user = request.user).role
			cur_time = timezone.localtime(timezone.now())
			if problem.test.end_time >= cur_time and role == 'student':
				return HttpResponseRedirect(reverse('index'))
			user_code = request.POST.get('code')
			author_code = problem.data['solution']
			cnt = 0
			for test in problem.data['tests']:
				user_output = execute(user_code, 'c', test)
				author_output = execute(author_code, 'c', test)
				if author_output == user_output:
					cnt += 1
				else:
					break
			score = problem.data['marks'] if cnt == len(problem.data['tests']) else 0

			submission = Submission(
				user = request.user,
				problem = problem,
				submission_time = timezone.now(),
				solution = user_code,
				score = score
			)
			submission.save()

			return HttpResponseRedirect(reverse('submission', args = (problem_link,)))

	except Exception as e:
		return HttpResponse('Problem not found')
	return render(request, 'grader/problem.html', context=context)

@login_required
def submission(request, problem_link):
	try:
		problem = Problem.objects.get(link = problem_link)
		role = UserRole.objects.get(user = request.user).role
		if problem.test.end_time >= cur_time and role == 'student':
			return HttpResponseRedirect(reverse('index'))
		submissions = Submission.objects.all().filter(user = request.user)
		submissions = submissions.filter(problem = problem)
		submissions = submissions.order_by('-submission_time')
		context = {
			'title': 'Submissions - ' + problem.title,
			'problem_link': problem_link,
			'submissions': submissions
		}

	except Exception as e:
		return HttpResponse('Problem not found')
	return render(request, 'grader/submission.html', context=context)

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
		start_time = pytz.timezone('Asia/Kolkata').localize(datetime.datetime.strptime(request.POST.get('starttime'), '%Y-%m-%dT%H:%M'))
		link = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

		test = Test(
			user = request.user,
			title = title,
			link = link,
			semester = semester,
			branch = branch,
			duration = duration,
			start_time = start_time,
			end_time = start_time + datetime.timedelta(minutes = duration)
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

@login_required
def result(request, test_link):

	try:
		role = UserRole.objects.get(user = request.user).role
		if role == 'student':
			return HttpResponseRedirect(reverse('test', args = (test_link,)))

		test = Test.objects.get(link = test_link)
		cur_time = timezone.localtime(timezone.now())
		if test.end_time >= cur_time:
			return HttpResponseRedirect(reverse('test', args = (test_link,)))

		students = StudentDetail.objects.all().filter(semester = test.semester)
		students = students.filter(branch = test.branch)
		problems = Problem.objects.all().filter(test = test)

		result = []
		for student in students:
			username = student.user.username
			cur = dict()
			cur['username'] = username
			cur['score'] = 0
			for problem in problems:
				sub = Submission.objects.all().filter(user = student.user)
				sub = sub.filter(problem = problem)
				sub = sub.order_by('-score')
				if len(sub) > 0:
					cur['score'] += sub.first().score
			result.append(cur)

		total = sum([problem.data['marks'] for problem in problems])

		context = {
			'title': test.title + ' - Result',
			'total': total,
			'test_link': test_link,
			'result': result
		}
		return render(request, 'grader/result.html', context=context)
	except:
		return HttpResponse('Error while loading the test')
