# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0013_auto_20151126_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='paper',
            field=models.ForeignKey(to='anarxiv_app.Paper'),
        ),
    ]
