# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0009_auto_20151201_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='area',
        ),
    ]
