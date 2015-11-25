# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0009_post_date'),
    ]

    operations = [
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
            name='dnVotes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='paper',
            field=models.ForeignKey(default=0, to='anarxiv_app.Paper'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='upVotes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.today, verbose_name=b'date published'),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.OneToOneField(default=0, to='anarxiv_app.User'),
            preserve_default=False,
        ),
    ]
