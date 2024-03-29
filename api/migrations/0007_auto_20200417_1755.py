# Generated by Django 3.0.5 on 2020-04-17 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20200417_1750'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Post')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.User')),
            ],
        ),
    ]
