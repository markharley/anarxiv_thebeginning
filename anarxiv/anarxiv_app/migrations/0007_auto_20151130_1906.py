# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0006_paper_journal'),
    ]

    operations = [
        migrations.CreateModel(
            name='newPaper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(null=True)),
                ('abstract', models.TextField(null=True)),
                ('journal', models.TextField(null=True)),
                ('Inspires_no', models.CharField(max_length=100, null=True)),
                ('arxiv_no', models.CharField(max_length=50, null=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='newarticles',
            field=models.ManyToManyField(to='anarxiv_app.newPaper'),
        ),
    ]
