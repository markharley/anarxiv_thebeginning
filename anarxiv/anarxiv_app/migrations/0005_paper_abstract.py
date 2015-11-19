# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0004_auto_20151119_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='abstract',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
