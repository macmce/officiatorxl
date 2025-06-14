# Generated by Django 5.2.1 on 2025-05-28 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0012_event_alter_meet_meet_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='duration_minutes',
        ),
        migrations.RemoveField(
            model_name='event',
            name='officials_required',
        ),
        migrations.RemoveField(
            model_name='event',
            name='participant_count',
        ),
        migrations.AlterField(
            model_name='event',
            name='meet_type',
            field=models.CharField(choices=[('dual', 'Dual'), ('divisional', 'Divisional')], default='dual', max_length=20),
        ),
    ]
