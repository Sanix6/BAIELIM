# Generated by Django 4.0.10 on 2024-05-23 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_remove_store_docs_store_documents'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='oneC_code',
            field=models.CharField(blank=True, max_length=250, verbose_name='1С код'),
        ),
    ]
