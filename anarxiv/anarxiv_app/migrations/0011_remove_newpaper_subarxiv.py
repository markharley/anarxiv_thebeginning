# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0010_remove_paper_area'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newpaper',
            name='subarxiv',
        ),
    ]
