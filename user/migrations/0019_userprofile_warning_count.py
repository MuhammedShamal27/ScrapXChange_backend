# Generated by Django 5.0.7 on 2024-10-02 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='warning_count',
            field=models.IntegerField(default=0),
        ),
    ]
