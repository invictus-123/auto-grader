# Full Featured Auto-Grader App

## Installation

### Step 1: Clone the repository
```bash
$ git clone https://github.com/invictus-123/auto-grader.git
$ cd auto-grader
```

### Step 2: Setup the virtual enivronment
```bash
$ python3 -m venv env
$ source env/bin/activate

```

### Step 3: Install dependencies
```bash
(env)$ pip install -r requirements.txt
```

## Running locally

### Step 1: Migrate the database
```bash
(env)$ python manage.py makemigrations
(env)$ python manage.py makemigrations grader
(env)$ python manage.py migrate
```

### Step 2: Run the server
```bash
(env)$ python manage.py runserver
```

## Features

### Signin/Signup
Users can signin/signup as a teacher or a student.

### Create Tests and Problems
Teachers can create tests and problems(Coding and MCQ).

### Edit Tests and Problems
Teachers can edit the tests or problems before the test starts.

### Delete Tests and Problems
Teachers can delete the tests or problems before the test starts.

### Test list view
A teacher can see all the tests that were created by them.
A student can see all the current and upcoming tests which are intended for their branch and semester.

### Problem list view
Students and teachers can see the list of all problems under a particular test.

### Solve Problems
Students can attempt and solve problems during the test in any of the available languages(C and Python3).

### Submitting a coding problem
Students and teachers can see the submission page after submitting a coding problem, that shows the time of submission,
verdict and score.

### Code Editor
The code editor loads the previous submitted code. It includes basic features such as auto indentation and adding closing
brackets.

### Submitting an MCQ question
Students and teachers can submit or clear the response of an MCQ question.

### Generate Result
Teacher can automatically generate the result once the test is over.

### Pagination
Tests, problems, submissions and result are limited to 5 to 10 entries per page.

### Responsive
The application is fully responsive and is tested on Chrome, Firefox and Opera.

## Tech Stacks
* **Frontend:** HTML, CSS, Bootstrap 4, JavaScript, jQuery
* **Language:** Python 3.6
* **Framework:** Django 3.0
* **Database:** SQLite3

## Deployment
Heroku link: [https://radiant-wildwood-82518.herokuapp.com/](https://radiant-wildwood-82518.herokuapp.com/)
