# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstName', models.TextField(null=True)),
                ('secondName', models.TextField(null=True)),
                ('BAI', models.CharField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(null=True)),
                ('abstract', models.TextField(null=True)),
                ('Inspires_no', models.CharField(max_length=100, null=True)),
                ('arxiv_no', models.CharField(max_length=50, null=True)),
                ('Citation_count', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paperID', models.CharField(default=b'0', max_length=100)),
                ('message', models.TextField(default=b'')),
                ('date', models.DateTimeField(default=datetime.datetime.today, verbose_name=b'date published')),
                ('upVotes', models.IntegerField(default=0)),
                ('dnVotes', models.IntegerField(default=0)),
                ('paper', models.ForeignKey(to='anarxiv_app.Paper')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('username', models.CharField(max_length=30)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('is_admin', models.BooleanField(default=False)),
                ('isAcademic', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('passwordExpiry', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.OneToOneField(to='anarxiv_app.User'),
        ),
        migrations.AddField(
            model_name='author',
            name='articles',
            field=models.ManyToManyField(to='anarxiv_app.Paper'),
        ),
    ]
