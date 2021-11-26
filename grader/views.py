from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from grader.forms import UserForm, UserRoleForm, StudentDetailsForm
from grader.judge import execute
from grader.models import UserRole, StudentDetail, Test, Problem, Submission

import hashlib, random, datetime, pytz

def index(request):
	"""
	View to load the home page of the application.
	Loads a jumbotron a coursel and about the application if the user is not logged in.
	Loads the list of tests based on the role of the user.
	For teacher, fetches all the tests created by the user.
	For student, fetches all the tests intended for the student's branch and semester.
	"""

	context = {
		'title': 'Home'
	}

	# Checks if the user is logged in
	if request.user.username:
		username = request.user.username
		role = UserRole.objects.get(user = request.user).role
		context['role'] = role

		cur_time = timezone.localtime(timezone.now())
		if role == 'teacher':
			# List of tests created by the teacher
			tests = Test.objects.all().filter(user = request.user)
		else:
			# List of tests intended for student's branch and semester
			details = StudentDetail.objects.get(user = request.user)
			tests = Test.objects.all().filter(branch = details.branch)
			tests = tests.filter(semester = details.semester)
		context['is_teacher'] = True if role == 'teacher' else False

		# Order the tests such that the most recent ones are at the top
		tests = tests.order_by('-start_time')

		if len(tests) == 0:
			messages.info(request, 'No tests available')

		# Create pagiation with 5 tests per page
		page = request.GET.get('page', 1)
		paginator = Paginator(tests, 5)
		try:
			paginated_tests = paginator.page(page)
		except PageNotAnInteger:
			paginated_tests = paginator.page(1)
		except EmptyPage:
			paginated_tests = paginator.page(paginator.num_pages)
		context['tests'] = paginated_tests

	return render(request, 'grader/index.html', context=context)

def signin(request):
	"""
	View to allow the user to login to the application.
	If the user is already logged in, it redirects them to home page.
	"""

	context = {
		'title': 'Sign In',
	}

	# Redirect to home page if already logged in
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))

	# Execute if the form is submitted
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Authenticate the user
		user = authenticate(username = username, password = password)

		# Login the user
		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
		else:
			context['error'] = 'Invalid username or password.'

	return render(request, 'grader/signin.html', context=context)

def signup(request):
	"""
	View to allow a new user to register for the application.
	It enables the user to choose their role between student and teacher.
	If the user is already logged in, it redirects them to home page.
	"""

	# Redirect to home page if already logged in
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))

	# Execute if the form is submitted
	if request.method == 'POST':
		# Create three forms
		# 1. User details
		# 2. User role
		# 3. Student details (if applicable)
		user_form = UserForm(request.POST)
		role_form = UserRoleForm(request.POST)
		student_details_form = StudentDetailsForm(request.POST)

		if user_form.is_valid() and role_form.is_valid():
			# Save the user data
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			# Save the role
			role = role_form.save(commit = False)
			role.user = user
			role.save()

			# Save the student details if  the registered user is a student
			if(role_form.cleaned_data['role'] == 'student') and student_details_form.is_valid():
				detail = student_details_form.save(commit = False)
				detail.user = user
				detail.save()

			# Login the new user
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(username = username, password = password)

			if user:
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect(reverse('index'))

	else:
		# Create the form objects
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
	"""
	Logout the user if they are logged in.
	"""

	logout(request)
	return HttpResponseRedirect(reverse('index'))

@login_required
def test_view(request, test_link):
	"""
	View to open a test and list all it's problems.
	Allows teacher to edit test, create and delete problems if the test has not started.
	Allows students and teachers to view the result if the test is over.
	"""
	try:
		test = Test.objects.get(link = test_link)
		role = UserRole.objects.get(user = request.user).role
		cur_time = timezone.localtime(timezone.now())

		# Redirect to home page if a student opens the test before it starts
		if test.start_time >= cur_time and role == 'student':
			return HttpResponseRedirect(reverse('index'))

		# Redirect to home page if some other teacher tries to access the test data
		if test.user != request.user:
			return HttpResponseRedirect(reverse('index'))

		# Fetch the data of problems associated with the test
		problems = Problem.objects.all().filter(test = test)
		username = request.user.username

		# Arrange the problems such that MCQ are at the top, followed by coding problems
		problems = problems.order_by('-type')

		if len(problems) == 0:
			messages.info(request, 'No problems added to this test')

		is_teacher = True if role == 'teacher' else False
		not_started = True if test.start_time > cur_time else False
		has_ended = True if test.end_time <= cur_time else False

		if test.start_time <= cur_time and test.end_time >= cur_time and role == 'teacher':
			messages.info(request, 'Edit, delete and create options are disabled as the test has started')
		elif test.end_time <= cur_time and role == 'teacher':
			messages.info(request, 'Edit, delete and create options are disabled as the test has ended')
		elif test.end_time <= cur_time and role == 'student':
			messages.info(request, 'The test has ended')

		# Create pagiation with 5 problems per page
		page = request.GET.get('page', 1)
		paginator = Paginator(problems, 5)
		try:
			paginated_problems = paginator.page(page)
		except PageNotAnInteger:
			paginated_problems = paginator.page(1)
		except EmptyPage:
			paginated_problems = paginator.page(paginator.num_pages)

		context = {
			'title': 'Test - ' + test.title,
			'is_teacher': is_teacher,
			'test_link': test_link,
			'has_ended': has_ended,
			'not_started': not_started,
			'problems': paginated_problems
		}
		return render(request, 'grader/test.html', context=context)
	except Exception as e:
		print(e)
		return HttpResponse('Test not found')

@login_required
def problem_view(request, problem_link):
	"""
	View to open a problem and load it's statement and other components
	based on the problem type. If type is coding, loads the sample input
	output and the code editor. If the type is mcq, loads the 4 options and
	clear button.
	"""

	try:
		role = UserRole.objects.get(user = request.user).role
		problem = Problem.objects.get(link = problem_link)
		cur_time = timezone.localtime(timezone.now())

		# Redirect to home page if a student opens the problem before it starts
		if problem.test.start_time >= cur_time and role == 'student':
			return HttpResponseRedirect(reverse('index'))

		# Redirect to home page if some other teacher tries to access the test data
		if problem.test.user != request.user:
			return HttpResponseRedirect(reverse('index'))

		is_teacher = True if role == 'teacher' else False
		not_started = True if problem.test.start_time > cur_time else False

		# Fetch the most recent submission by the user
		user_sub = Submission.objects.all().filter(problem = problem)
		user_sub = user_sub.filter(user = request.user)
		user_sub = user_sub.order_by('-submission_time')

		if problem.type == 'coding':
			sample_output = execute(problem.data['solution'], problem.data['language'], problem.data['sample_input'])
			context = {
				'title': 'Problem - ' + problem.title,
				'problem': problem,
				'test_link': problem.test.link,
				'sample_output': sample_output,
				'is_teacher': is_teacher,
				'not_started': not_started
			}
		else:
			context = {
				'title': 'Problem - ' + problem.title,
				'problem': problem,
				'test_link': problem.test.link,
				'is_teacher': is_teacher,
				'not_started': not_started
			}

		if len(user_sub) > 0:
			context['user_sub'] = user_sub.first()

		# Execute if the form is submitted
		if request.method == 'POST':

			# Redirect to home page if a student opens the problem before it starts
			if problem.test.start_time >= cur_time and role == 'student':
				return HttpResponseRedirect(reverse('index'))

			if problem.type == 'coding':
				# Run all the test cases if problem type is coding
				user_code = request.POST.get('code')
				author_code = problem.data['solution']
				cnt = 0
				verdict = 'accepted'
				for test in problem.data['tests']:
					user_output = execute(user_code, request.POST.get('language'), test).rstrip("\n")
					author_output = execute(author_code, problem.data['language'], test).rstrip("\n")
					if author_output == user_output:
						cnt += 1
					else:
						if user_output in ['compilation error', 'runtime error', 'time limit exceeded']:
							verdict = user_output
						break
				score = problem.data['marks'] if cnt == len(problem.data['tests']) else 0

				if score == 0 and verdict == 'accepted':
					verdict = 'wrong answer'

				submission = Submission(
					user = request.user,
					problem = problem,
					submission_time = timezone.now(),
					type = 'coding',
					verdict = verdict,
					language = request.POST.get('language'),
					solution = user_code,
					score = score
				)
				submission.save()
				return HttpResponseRedirect(reverse('submission', args = (problem_link,)))
			else:
				# Match the user's selected option with the answer
				if 'option' in request.POST:
					selected_option = request.POST.get('option')
				else:
					selected_option = 'unattempted'
				score = problem.data['marks'] if selected_option == problem.data['answer'] else 0
				submission = Submission(
					user = request.user,
					problem = problem,
					submission_time = timezone.now(),
					type = 'mcq',
					solution = selected_option,
					score = score
				)
				submission.save()
				return HttpResponseRedirect(reverse('test', args = (problem.test.link,)))

	except Exception as e:
		print(e)
		return HttpResponse('Problem not found')
	return render(request, 'grader/problem.html', context=context)

@login_required
def submission(request, problem_link):
	"""
	View for display a list of submissions by the user if the problem
	type is coding. Redirects to test view if the problem type is mcq.
	"""

	try:
		problem = Problem.objects.get(link = problem_link)
		# Redirect to problem view if type is mcq
		if problem.type == 'mcq':
			return HttpResponseRedirect(reverse('problem', args = (problem_link,)))

		role = UserRole.objects.get(user = request.user).role
		cur_time = timezone.localtime(timezone.now())

		# Redirect to home page if a student opens the list before the test starts
		if problem.test.start_time >= cur_time and role == 'student':
			return HttpResponseRedirect(reverse('index'))

		# Fetch all the submissions and order them such that most recent ones are at the top
		submissions = Submission.objects.all().filter(user = request.user)
		submissions = submissions.filter(problem = problem)
		submissions = submissions.order_by('-submission_time')

		# Create pagiation with 10 submissions per page
		page = request.GET.get('page', 1)
		paginator = Paginator(submissions, 10)
		try:
			paginated_submissions = paginator.page(page)
		except PageNotAnInteger:
			paginated_submissions = paginator.page(1)
		except EmptyPage:
			paginated_submissions = paginator.page(paginator.num_pages)

		context = {
			'title': 'Submissions - ' + problem.title,
			'problem_link': problem_link,
			'submissions': paginated_submissions
		}

	except Exception as e:
		print(e)
		return HttpResponse('Problem not found')
	return render(request, 'grader/submission.html', context=context)

@login_required
def create_test(request):
	"""
	View to allow teacher to create a new test from the home page.
	Redirects to home page if the user is student.
	"""

	role = UserRole.objects.get(user = request.user).role

	# Redirect to home page if student tries to create a test
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	# If the form is submitted
	if request.method == 'POST':

		# Gather all the required information
		title = request.POST.get('title')
		semester = request.POST.get('semester')
		branch = request.POST.get('branch')
		duration = int(request.POST.get('duration'))
		start_time = pytz.timezone('Asia/Kolkata').localize(datetime.datetime.strptime(request.POST.get('starttime'), '%Y-%m-%dT%H:%M'))
		link = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

		# Create a test object and save it to the database
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

		# Redirect back to home page
		return HttpResponseRedirect(reverse('index'))

	context = {
		'title': 'Create Test',
	}
	return render(request, 'grader/create_test.html', context=context)

@login_required
def create_problem(request, test_link):
	"""
	View to allow the teacher to create coding and mcq problems in a test.
	Redirects back to test view if the test has started or ended.
	Redirects back to test view if a student tries to create a problem.
	"""

	role = UserRole.objects.get(user = request.user).role

	# Redirect to test view if student tries to create a problem
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	test = Test.objects.get(link = test_link)

	# Redirect to home page if some other teacher tries to access the test data
	if test.user != request.user:
		return HttpResponseRedirect(reverse('index'))

	cur_time = timezone.localtime(timezone.now())

	# Redirect to test view if the test has started or ended
	if test.start_time <= cur_time:
		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	# Redirect to home page if some other teacher tries to access the test data
	if test.user != request.user:
		return HttpResponseRedirect(reverse('index'))

	# If the form is  submitted
	if request.method == 'POST':

		# Gather all the required  information
		title = request.POST.get('title')
		statement = request.POST.get('statement')
		problem_type = request.POST.get('type')
		marks = int(request.POST.get('marks'))
		link = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

		# Create a problem object and save it to the database
		# Data of the problem depends on the type of problem
		if problem_type == 'coding':
			test_cases = request.POST.getlist('test-case')
			sample_input = request.POST.get('sample-input')
			language = request.POST.get('language')
			solution = request.POST.get('code')
			data = {
				'statement': statement,
				'sample_input': sample_input,
				'tests': test_cases,
				'language': language,
				'solution': solution,
				'marks': marks
			}
		else:
			option1 = request.POST.get('option1')
			option2 = request.POST.get('option2')
			option3 = request.POST.get('option3')
			option4 = request.POST.get('option4')
			answer = request.POST.get('answer')
			data = {
				'statement': statement,
				'option1': option1,
				'option2': option2,
				'option3': option3,
				'option4': option4,
				'answer': answer,
				'marks': marks
			}

		prob = Problem(
			test = test,
			title = title,
			type = problem_type,
			link = link,
			data = data
		)
		prob.save()

		# Redirect back to the test view
		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	context = {
		'title': test.title + ' - Create Problem',
		'test_link': test_link,
	}
	return render(request, 'grader/create_problem.html', context=context)

@login_required
def result(request, test_link):
	"""
	View to display the result once the test is over.
	Redirects back to test view if the test hasn't ended.
	"""

	try:
		role = UserRole.objects.get(user = request.user).role

		test = Test.objects.get(link = test_link)
		cur_time = timezone.localtime(timezone.now())

		# Redirect to test view if test has not ended
		if test.end_time >= cur_time:
			return HttpResponseRedirect(reverse('test', args = (test_link,)))

		# Fetch the list  of students and problems
		students = StudentDetail.objects.all().filter(semester = test.semester)
		students = students.filter(branch = test.branch)
		problems = Problem.objects.all().filter(test = test)

		# Generate result for each student
		# Marking Scheme -
		# Coding: Best submission by score is connsidered
		# MCQ: Most recent submission is considered
		result = []
		for student in students:
			username = student.user.username
			cur = dict()
			cur['username'] = username
			cur['score'] = 0
			for problem in problems:
				sub = Submission.objects.all().filter(user = student.user)
				sub = sub.filter(problem = problem)
				sub = sub.filter(submission_time__lt = problem.test.end_time)
				if problem.type == 'coding':
					sub = sub.order_by('-score')
				else:
					sub = sub.order_by('-submission_time')
				if len(sub) > 0:
					cur['score'] += sub.first().score
			result.append(cur)

		result = sorted(result, key = lambda x: x['score'], reverse = True)

		# Calculate rank of each student
		for i in range(len(result)):
			if i == 0:
				result[i]['rank'] = i + 1
			else:
				if result[i]['score'] == result[i - 1]['score']:
					result[i]['rank'] = result[i - 1]['rank']
				else:
					result[i]['rank'] = i + 1

		# Calculate total score
		total = sum([problem.data['marks'] for problem in problems])

		# Create pagiation with 10 entries per page
		page = request.GET.get('page', 1)
		paginator = Paginator(result, 10)
		try:
			paginated_result = paginator.page(page)
		except PageNotAnInteger:
			paginated_result = paginator.page(1)
		except EmptyPage:
			paginated_result = paginator.page(paginator.num_pages)

		context = {
			'title': test.title + ' - Result',
			'total': total,
			'test_link': test_link,
			'result': paginated_result
		}
		return render(request, 'grader/result.html', context=context)
	except Exception as e:
		print(e)
		return HttpResponse('Error while loading the result')

@login_required
def delete_test(request, test_link):
	"""
	View to delete the test, all it's problems and submissions.
	Redirects to home page if a student tries to delete a test.
	Redirects to test view if a user tries to delete a test after it has started.
	"""

	role = UserRole.objects.get(user = request.user).role

	# Redirect to home page if student tries to delete a test
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	test = Test.objects.get(link = test_link)

	# Redirect to home page if some other teacher tries to access the test data
	if test.user != request.user:
		return HttpResponseRedirect(reverse('index'))

	cur_time = timezone.localtime(timezone.now())

	# Redirect to test view if test has started
	if test.start_time <= cur_time:
		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	# If confirmation form is submitted
	if request.method == 'POST':
		if 'yes' in request.POST:
			# Delete the test
			test.delete()
			return HttpResponseRedirect(reverse('index'))
		else:
			return HttpResponseRedirect(reverse('test', args = (test_link,)))

	context = {
		'title': test.title + ' - Delete',
	}

	return render(request, 'grader/delete.html', context=context)

@login_required
def delete_problem(request, problem_link):
	"""
	View to delete the problem and all it's submissions.
	Redirects to home page if a student tries to delete a test.
	Redirects to problem view if a user tries to delete a test after it has started.
	"""

	role = UserRole.objects.get(user = request.user).role

	# Redirect to home page if student tries to delete a problem
	if role == 'student':
		return HttpResponseRedirect(reverse('index'))

	problem = Problem.objects.get(link = problem_link)

	# Redirect to home page if some other teacher tries to access the test data
	if problem.test.user != request.user:
		return HttpResponseRedirect(reverse('index'))

	cur_time = timezone.localtime(timezone.now())

	# Redirect to problem view if test has started
	if problem.test.start_time <= cur_time:
		return HttpResponseRedirect(reverse('problem', args = (problem_link,)))

	# If confirmation form is submitted
	if request.method == 'POST':
		if 'yes' in request.POST:
			# Delete the problem
			problem.delete()
			return HttpResponseRedirect(reverse('test', args = (problem.test.link,)))
		else:
			return HttpResponseRedirect(reverse('problem', args = (problem_link,)))

	context = {
		'title': problem.title + ' - Delete',
	}

	return render(request, 'grader/delete.html', context=context)

@login_required
def edit_test(request, test_link):
	"""
	View to edit the properties of a test.
	Redirects to test view if a student tries to edit the test.
	Redirects to test view if a user tries to edit a test that has already started.
	"""

	role = UserRole.objects.get(user = request.user).role

	# Redirect to test view if a student tries to edit a test
	if role == 'student':
		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	test = Test.objects.get(link = test_link)

	# Redirect to home page if some other teacher tries to access the test data
	if test.user != request.user:
		return HttpResponseRedirect(reverse('index'))

	cur_time = timezone.localtime(timezone.now())

	# Redirect to test view if test has already started
	if test.start_time <= cur_time:
		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	# If the form is submitted
	if request.method == 'POST':
		# Gather all the required information
		test.title = request.POST.get('title')
		test.semester = request.POST.get('semester')
		test.branch = request.POST.get('branch')
		test.duration = int(request.POST.get('duration'))
		test.end_time = test.start_time + datetime.timedelta(minutes = int(request.POST.get('duration')))

		# Save the test
		test.save()

		return HttpResponseRedirect(reverse('test', args = (test_link,)))

	context = {
		'title': test.title + ' - Edit',
		'test': test
	}
	return render(request, 'grader/edit_test.html', context=context)

@login_required
def edit_problem(request, problem_link):
	"""
	View to edit the properties of a problem.
	Redirects to problem view if a student tries to edit the problem.
	Redirects to problem view if a user tries to edit the problem,
	for which the test has already started.
	"""

	role = UserRole.objects.get(user = request.user).role

	# Redirect to problem view if a student tries to edit a problem
	if role == 'student':
		return HttpResponseRedirect(reverse('problem', args = (problem_link,)))

	problem = Problem.objects.get(link = problem_link)

	# Redirect to home page if some other teacher tries to access the test data
	if problem.test.user != request.user:
		return HttpResponseRedirect(reverse('index'))

	cur_time = timezone.localtime(timezone.now())

	# Redirect to problem view if test has already started
	if problem.test.start_time <= cur_time:
		return HttpResponseRedirect(reverse('problem', args = (problem_link,)))

	# If the form is submitted
	if request.method == 'POST':
		# Gather required information for coding problem
		problem.title = request.POST.get('title')
		problem.type = request.POST.get('type')
		marks = int(request.POST.get('marks'))

		statement = request.POST.get('statement')

		if request.POST.get('type') == 'coding':
			test_cases = request.POST.getlist('test-case')
			sample_input = request.POST.get('sample-input')
			language = request.POST.get('language')
			solution = request.POST.get('code')
			problem.data = {
				'statement': statement,
				'sample_input': sample_input,
				'tests': test_cases,
				'language': language,
				'solution': solution,
				'marks': marks
			}
		else:
			# Gather required information for MCQ problem
			option1 = request.POST.get('option1')
			option2 = request.POST.get('option2')
			option3 = request.POST.get('option3')
			option4 = request.POST.get('option4')
			answer = request.POST.get('answer')
			problem.data = {
				'statement': statement,
				'option1': option1,
				'option2': option2,
				'option3': option3,
				'option4': option4,
				'answer': answer,
				'marks': marks
			}

		# Save the problem
		problem.save()

		return HttpResponseRedirect(reverse('problem', args = (problem_link,)))

	context = {
		'title': problem.title + ' - Edit',
		'problem': problem
	}
	return render(request, 'grader/edit_problem.html', context=context)
