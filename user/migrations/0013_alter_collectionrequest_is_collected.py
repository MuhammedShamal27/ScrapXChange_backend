# Generated by Django 5.0.7 on 2024-08-28 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_collectionrequest_is_collected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionrequest',
            name='is_collected',
            field=models.BooleanField(default=False),
        ),
    ]