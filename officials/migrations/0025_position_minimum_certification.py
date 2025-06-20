# Generated by Django 5.2.1 on 2025-06-10 04:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0024_eventposition_position_events'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='minimum_certification',
            field=models.ForeignKey(blank=True, help_text='The minimum certification level required for this position', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='required_positions', to='officials.certification'),
        ),
    ]
