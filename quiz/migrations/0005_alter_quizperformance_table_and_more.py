# Generated by Django 5.0.6 on 2024-05-28 06:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_scheduledevent_quizperformance'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='quizperformance',
            table='QUIZ_PERFORMANCE',
        ),
        migrations.AlterModelTable(
            name='scheduledevent',
            table='SCHEDULED_EVENTS',
        ),
    ]
