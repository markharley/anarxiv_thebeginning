# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0008_newpaper_subarxiv'),
    ]

    operations = [
        migrations.CreateModel(
            name='subArxiv',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='newpaper',
            name='area',
            field=models.ManyToManyField(to='anarxiv_app.subArxiv'),
        ),
        migrations.AddField(
            model_name='paper',
            name='area',
            field=models.ManyToManyField(to='anarxiv_app.subArxiv'),
        ),
    ]
