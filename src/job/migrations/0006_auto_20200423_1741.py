# Generated by Django 2.2.2 on 2020-04-23 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0005_country_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicaljob',
            old_name='cityname',
            new_name='_cities',
        ),
        migrations.RenameField(
            model_name='historicaljob',
            old_name='countryname',
            new_name='_country',
        ),
        migrations.RenameField(
            model_name='historicaljob',
            old_name='provincename',
            new_name='_province',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='cityname',
            new_name='_cities',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='countryname',
            new_name='_country',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='provincename',
            new_name='_province',
        ),
    ]