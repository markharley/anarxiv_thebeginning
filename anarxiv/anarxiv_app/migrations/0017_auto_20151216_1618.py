# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0016_auto_20151216_1359'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='newpaper',
            new_name='new_paper',
        ),
    ]
