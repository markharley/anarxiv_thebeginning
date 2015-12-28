# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0017_auto_20151216_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='newpaper',
            name='created_at',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
