# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0010_auto_20151125_2328'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='recordID',
            new_name='Inspires_ID',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='paperID',
            new_name='Inspires_ID',
        ),
        migrations.AddField(
            model_name='paper',
            name='arxiv_no',
            field=models.CharField(default='0', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='paper',
            field=models.ForeignKey(to='anarxiv_app.Paper'),
        ),
    ]
