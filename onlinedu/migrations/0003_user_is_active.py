# Generated by Django 3.0.7 on 2020-07-24 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0002_remove_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
