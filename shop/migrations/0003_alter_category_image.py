# Generated by Django 5.0.7 on 2024-11-15 13:39

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_shop_latitude_alter_shop_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, verbose_name='image'),
        ),
    ]