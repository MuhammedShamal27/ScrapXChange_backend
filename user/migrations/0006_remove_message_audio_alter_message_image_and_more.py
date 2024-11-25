# Generated by Django 5.0.7 on 2024-11-15 10:49

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='audio',
        ),
        migrations.AlterField(
            model_name='message',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='message',
            name='video',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='videos'),
        ),
    ]