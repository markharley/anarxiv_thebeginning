# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0015_post_newpaper'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='newpaper',
            field=models.ForeignKey(to='anarxiv_app.newPaper', null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='paper',
            field=models.ForeignKey(to='anarxiv_app.Paper', null=True),
        ),
    ]
