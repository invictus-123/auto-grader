# Generated by Django 3.0 on 2021-11-21 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0007_submission_submission_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='submission_time',
            field=models.DateTimeField(),
        ),
    ]