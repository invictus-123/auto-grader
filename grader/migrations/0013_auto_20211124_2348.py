# Generated by Django 3.0 on 2021-11-24 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0012_auto_20211124_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='solution',
            field=models.TextField(default='unattempted'),
        ),
    ]
