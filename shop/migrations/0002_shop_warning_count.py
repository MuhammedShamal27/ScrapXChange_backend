# Generated by Django 5.0.7 on 2024-10-02 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='warning_count',
            field=models.IntegerField(default=0),
        ),
    ]
