# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0002_auto_20151119_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='recordID',
            field=models.CharField(default='0', max_length=100),
            preserve_default=False,
        ),
    ]
