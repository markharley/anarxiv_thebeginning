# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0018_newpaper_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newpaper',
            name='created_at',
        ),
        migrations.AddField(
            model_name='newpaper',
            name='new',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
