# Generated by Django 5.1.6 on 2025-02-23 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_remove_certificate_study_center'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalset',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='socialstatus',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
    ]
