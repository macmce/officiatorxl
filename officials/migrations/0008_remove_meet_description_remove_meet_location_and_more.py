# Generated by Django 5.2.1 on 2025-05-15 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0007_pool'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meet',
            name='description',
        ),
        migrations.RemoveField(
            model_name='meet',
            name='location',
        ),
        migrations.RemoveField(
            model_name='meet',
            name='start_time',
        ),
        migrations.AddField(
            model_name='meet',
            name='meet_type',
            field=models.CharField(choices=[('Dual', 'Dual'), ('Divisional', 'Divisional'), ('Other', 'Other')], default='Dual', max_length=10),
        ),
        migrations.AlterField(
            model_name='pool',
            name='bidirectional',
            field=models.BooleanField(default=False, help_text='Do you start events at both ends of the pool?'),
        ),
    ]
