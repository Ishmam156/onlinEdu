# Generated by Django 3.0.7 on 2020-07-30 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0021_course_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='video',
            field=models.URLField(blank=True),
        ),
    ]
