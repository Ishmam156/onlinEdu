# Generated by Django 3.0.7 on 2020-07-27 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0019_auto_20200727_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
    ]