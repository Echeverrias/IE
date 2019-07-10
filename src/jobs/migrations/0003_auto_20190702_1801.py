# Generated by Django 2.2.2 on 2019-07-02 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_company_company_offers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(choices=[('ofertas-internacionales', 'Empleo internacional'), ('trabajo', 'Empleo nacional'), ('primer-empleo', 'Primer empleo')], default='trabajo', max_length=23),
        ),
    ]
