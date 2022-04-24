# Generated by Django 3.2.6 on 2022-04-24 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital_hub', '0004_speciality_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_reviews', to='hospital_hub.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_comments', to='hospital_hub.patient')),
            ],
        ),
    ]
