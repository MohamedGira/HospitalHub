# Generated by Django 3.2.6 on 2022-04-27 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital_hub', '0012_auto_20220427_0239'),
    ]

    operations = [
        migrations.AddField(
            model_name='speciality',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='media/'),
        ),
    ]
