# Generated by Django 4.0.10 on 2024-06-24 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_orderhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='weight',
            field=models.FloatField(default=0, verbose_name='Вес'),
        ),
    ]
