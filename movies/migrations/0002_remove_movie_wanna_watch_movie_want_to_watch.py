# Generated by Django 4.1.4 on 2023-08-16 15:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='wanna_watch',
        ),
        migrations.AddField(
            model_name='movie',
            name='want_to_watch',
            field=models.ManyToManyField(blank=True, related_name='want_to_watch', to=settings.AUTH_USER_MODEL),
        ),
    ]
