# Generated by Django 5.1.6 on 2025-03-08 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_alter_certificate_social_status_delete_socialstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(upload_to='courses'),
        ),
    ]
