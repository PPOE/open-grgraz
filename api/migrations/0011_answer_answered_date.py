# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-07 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20160919_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answered_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]