# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-28 10:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20160728_1016'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='motion',
            name='answer',
        ),
        migrations.AddField(
            model_name='motion',
            name='answers',
            field=models.ManyToManyField(blank=True, null=True, to='api.Answer'),
        ),
    ]
