# Generated by Django 5.2.1 on 2025-05-15 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0004_auto_20250515_0345'),
    ]

    operations = [
        # Add abbreviation field to Certification model
        migrations.AddField(
            model_name='certification',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=3),
        ),
    ]
