# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0013_auto_20151214_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpaper',
            name='added_at',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
