# Generated by Django 3.0.5 on 2020-05-03 06:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20200503_0128'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_requested', models.DateTimeField(default=django.utils.timezone.now)),
                ('initiator_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initiator_user_id', to='api.User')),
                ('target_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_user_id', to='api.User')),
            ],
        ),
    ]
