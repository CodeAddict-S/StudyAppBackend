# Generated by Django 5.1.6 on 2025-02-25 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_generalset_status_alter_socialstatus_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='certificate',
            options={'verbose_name': 'Sertifikat', 'verbose_name_plural': 'Sertifikatlar'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name': 'Kurs', 'verbose_name_plural': 'Kurslar'},
        ),
        migrations.AlterModelOptions(
            name='generalset',
            options={'verbose_name': 'General set', 'verbose_name_plural': 'General sets'},
        ),
        migrations.AlterModelOptions(
            name='socialstatus',
            options={'verbose_name': 'Social status', 'verbose_name_plural': 'Social statuses'},
        ),
        migrations.AlterModelOptions(
            name='studycenter',
            options={'verbose_name': "O'quv Markaz", 'verbose_name_plural': "O'quv Markazlari"},
        ),
    ]
