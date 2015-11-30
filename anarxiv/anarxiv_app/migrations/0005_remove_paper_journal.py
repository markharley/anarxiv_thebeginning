# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0004_paper_journal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='journal',
        ),
    ]
