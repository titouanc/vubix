# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20150921_2201'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='schedule',
            unique_together=set([]),
        ),
    ]
