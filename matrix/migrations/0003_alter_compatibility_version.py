# Generated by Django 5.1.4 on 2025-01-11 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0002_alter_compatibility_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compatibility',
            name='version',
            field=models.CharField(blank=True, help_text='example: 3.2.5', max_length=100, null=True),
        ),
    ]
