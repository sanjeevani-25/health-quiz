# Generated by Django 5.0.6 on 2024-05-27 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0003_alter_user_last_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
