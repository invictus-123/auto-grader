# Generated by Django 3.0 on 2021-11-21 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0008_auto_20211121_1450'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='has_expired',
        ),
    ]
