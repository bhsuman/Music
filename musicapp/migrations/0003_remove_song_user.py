# Generated by Django 2.2.13 on 2023-05-17 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicapp', '0002_ram'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='user',
        ),
    ]
