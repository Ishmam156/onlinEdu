# Generated by Django 3.0.7 on 2020-07-27 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0018_auto_20200726_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.TextField(unique=True),
        ),
    ]
