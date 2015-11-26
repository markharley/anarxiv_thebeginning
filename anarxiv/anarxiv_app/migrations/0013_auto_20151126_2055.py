# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0012_auto_20151126_2052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='Inspires_ID',
            new_name='recordID',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='Inspires_ID',
            new_name='paperID',
        ),
        migrations.AlterField(
            model_name='paper',
            name='arxiv_no',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='post',
            name='paper',
            field=models.ForeignKey(to='anarxiv_app.Paper'),
        ),
    ]
