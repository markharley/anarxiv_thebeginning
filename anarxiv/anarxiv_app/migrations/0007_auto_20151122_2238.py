# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anarxiv_app', '0006_paper_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paperID', models.CharField(default=b'0', max_length=100)),
                ('message', models.TextField(default=b'')),
            ],
        ),
        migrations.AlterField(
            model_name='paper',
            name='messages',
            field=models.TextField(default=b''),
        ),
    ]
