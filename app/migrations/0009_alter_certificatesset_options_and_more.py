# Generated by Django 5.1.6 on 2025-02-27 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_rename_generalset_certificatesset'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='certificatesset',
            options={'verbose_name': 'Certificates set', 'verbose_name_plural': 'Certificates sets'},
        ),
        migrations.RemoveField(
            model_name='certificate',
            name='gender',
        ),
    ]
