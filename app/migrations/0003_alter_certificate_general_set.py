# Generated by Django 5.1.6 on 2025-02-20 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_certificate_general_set'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='general_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='app.generalset'),
        ),
    ]
