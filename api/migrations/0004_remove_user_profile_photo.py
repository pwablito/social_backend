# Generated by Django 3.0.5 on 2020-04-17 05:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200417_0507'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_photo',
        ),
    ]
