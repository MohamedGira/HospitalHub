# Generated by Django 3.2.6 on 2022-05-06 11:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hospital_hub', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='age',
        ),
    ]
