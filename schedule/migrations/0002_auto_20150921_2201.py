# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='schedule',
            unique_together=set([('course', 'start_time', 'end_time', 'location')]),
        ),
    ]
