# Generated by Django 4.0.10 on 2024-04-24 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_orderitem_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cost',
            options={'verbose_name': 'Цена', 'verbose_name_plural': 'Цены'},
        ),
    ]
