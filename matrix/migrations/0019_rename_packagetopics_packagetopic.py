# Generated by Django 5.1.4 on 2025-01-23 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0018_alter_packagerequest_django_compatible_versions_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PackageTopics',
            new_name='PackageTopic',
        ),
    ]
