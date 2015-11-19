# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0003_paper_recordid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='recordID',
            field=models.CharField(default=b'0', max_length=100),
        ),
    ]
