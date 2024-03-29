# Generated by Django 3.0.5 on 2020-04-17 05:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(default=datetime.datetime(2020, 4, 17, 5, 6, 38, 29368), max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='profile_photo',
            field=models.ImageField(default=None, upload_to=''),
            preserve_default=False,
        ),
    ]
