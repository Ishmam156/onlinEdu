# Generated by Django 3.0.7 on 2020-07-24 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0003_user_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]