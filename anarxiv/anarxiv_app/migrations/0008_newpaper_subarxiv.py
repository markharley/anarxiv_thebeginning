# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0007_auto_20151130_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='newpaper',
            name='subarxiv',
            field=models.TextField(null=True),
        ),
    ]
