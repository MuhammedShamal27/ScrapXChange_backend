# Generated by Django 5.0.7 on 2024-08-08 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_customuser_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='otp_generated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]