from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('QUADRANTS', 'Quadrants'), ('SIDES', 'Sides')], help_text='Officiating strategy (Quadrants or Sides)', max_length=20, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Strategy',
                'verbose_name_plural': 'Strategies',
                'ordering': ['name'],
            },
        ),
    ]
