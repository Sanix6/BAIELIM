# Generated by Django 4.0.10 on 2024-05-04 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_cost_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='lat',
            field=models.FloatField(default=0, verbose_name='LAT'),
        ),
        migrations.AddField(
            model_name='order',
            name='lon',
            field=models.FloatField(default=0, verbose_name='LON'),
        ),
    ]
