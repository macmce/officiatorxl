# Generated by Django 5.2.1 on 2025-06-21 02:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0027_strategy_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='meet',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meets', to='officials.division'),
        ),
    ]
