# Generated by Django 3.2.6 on 2022-05-11 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital_hub', '0005_auto_20220509_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='hospital_hub.schedule'),
        ),
        migrations.AlterField(
            model_name='appointmentdocument',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='medicaltest',
            name='result',
            field=models.FileField(blank=True, default=None, null=True, upload_to=''),
        ),
    ]
