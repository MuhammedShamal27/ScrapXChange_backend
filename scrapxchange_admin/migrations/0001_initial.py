# Generated by Django 5.0.7 on 2024-10-18 12:58

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
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('fraud', 'Fraud'), ('inappropriate', 'Inappropriate Content'), ('spam', 'Spam'), ('other', 'Other')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('is_checked', models.BooleanField(blank=True, default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_received', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_sent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
