# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0011_remove_newpaper_subarxiv'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subarxiv',
            old_name='title',
            new_name='region',
        ),
    ]
