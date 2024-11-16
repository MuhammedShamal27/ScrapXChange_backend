# Generated by Django 5.0.7 on 2024-11-15 14:59

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='profile_picture',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, verbose_name='image'),
        ),
    ]
