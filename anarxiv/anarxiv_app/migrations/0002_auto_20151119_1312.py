# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='bodytext',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='timestamp',
        ),
    ]
