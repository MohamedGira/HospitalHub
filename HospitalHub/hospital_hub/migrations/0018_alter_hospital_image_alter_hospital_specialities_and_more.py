# Generated by Django 4.0.4 on 2022-04-30 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital_hub', '0017_auto_20220430_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospital',
            name='image',
            field=models.ImageField(default='media/no_hospital_img.png', null=True, upload_to='media/'),
        ),
        migrations.AlterField(
            model_name='hospital',
            name='specialities',
            field=models.ManyToManyField(blank=True, to='hospital_hub.speciality'),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='media/no_profile_img.png', upload_to='media/'),
        ),
    ]
