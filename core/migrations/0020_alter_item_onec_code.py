# Generated by Django 4.0.10 on 2024-07-25 15:54

import core.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_item_onec_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='oneC_code',
            field=core.models.PreserveWhitespaceCharField(blank=True, max_length=250),
        ),
    ]
