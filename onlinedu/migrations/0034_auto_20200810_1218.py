# Generated by Django 3.0.7 on 2020-08-10 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0033_course_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=models.URLField(blank=True),
        ),
    ]
