# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0012_auto_20151201_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpaper',
            name='added_at',
            field=models.DateTimeField(null=True),
        ),
    ]
