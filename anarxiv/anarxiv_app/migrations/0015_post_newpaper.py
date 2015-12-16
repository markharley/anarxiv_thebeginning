# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0014_auto_20151214_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='newpaper',
            field=models.ForeignKey(default=0, to='anarxiv_app.newPaper'),
            preserve_default=False,
        ),
    ]
