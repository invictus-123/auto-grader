# Generated by Django 3.0 on 2021-11-16 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='branch',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='test',
            name='semester',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
