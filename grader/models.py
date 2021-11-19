from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User

# Create your models here.
class UserRole(models.Model):
    user =  models.OneToOneField(User, on_delete = models.CASCADE)
    role = models.CharField(max_length = 255)

    def __str__(self):
        return self.user.username

class StudentDetail(models.Model):
    user =  models.OneToOneField(User, on_delete = models.CASCADE)
    semester = models.IntegerField()
    branch = models.CharField(max_length = 255)

    def __str__(self):
        return self.user.username

class Test(models.Model):
    test_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 255)
    link = models.CharField(max_length = 255)
    semester = models.IntegerField()
    branch = models.CharField(max_length = 255)
    duration = models.IntegerField()
    start_time = models.DateTimeField()
    has_expired = models.BooleanField(default = False)

    def __str__(self):
        return self.title

class Problem(models.Model):
    problem_id = models.AutoField(primary_key = True)
    test = models.ForeignKey(Test, on_delete = models.CASCADE)
    title = models.CharField(max_length = 255)
    type = models.CharField(max_length = 255)
    link = models.CharField(max_length = 255)
    data = JSONField()

    def __str__(self):
        return str(self.problem_id)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    test = models.ForeignKey(Test, on_delete = models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete = models.CASCADE)
    solution = models.TextField(default = "")
    score = models.IntegerField(default = 0)
    after_completion = models.BooleanField(default = False)

    def __str__(self):
        return str(user) + " " + str(problem)

class TestSubmission(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    test = models.ForeignKey(Test, on_delete = models.CASCADE)

    def __str__(self):
        return str(user) + " " + str(test)
