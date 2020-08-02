# Generated by Django 3.0.7 on 2020-08-01 06:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinedu', '0032_auto_20200801_0408'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='completed',
            field=models.ManyToManyField(blank=True, related_name='completed_courses', to=settings.AUTH_USER_MODEL),
        ),
    ]
