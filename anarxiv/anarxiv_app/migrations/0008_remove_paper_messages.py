# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0007_auto_20151122_2238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='messages',
        ),
    ]
