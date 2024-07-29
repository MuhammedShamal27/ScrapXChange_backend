# Generated by Django 5.0.7 on 2024-07-28 06:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_name', models.CharField(max_length=33)),
                ('shop_license_number', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('address', models.TextField()),
                ('place', models.CharField(max_length=100)),
                ('profile_picture', models.ImageField(blank=True, upload_to='shop_pics')),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shop', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]