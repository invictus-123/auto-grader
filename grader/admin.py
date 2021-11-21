from django.contrib import admin
from grader.models import UserRole, StudentDetail, Test, Problem, Submission

# Register your models here.
admin.site.register(UserRole)
admin.site.register(StudentDetail)
admin.site.register(Test)
admin.site.register(Problem)
admin.site.register(Submission)
