# Generated by Django 4.0.10 on 2024-07-25 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_alter_item_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='code',
            field=models.CharField(blank=True, max_length=250, verbose_name='Наименование код'),
        ),
    ]
