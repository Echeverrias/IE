# Generated by Django 2.2.2 on 2019-11-24 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0010_auto_20191124_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaljob',
            name='category_level',
            field=models.CharField(choices=[('Mandos', 'Mandos'), ('Empleados', 'Empleados'), ('Técnicos', 'Técnicos'), ('Dirección', 'Dirección'), ('Sin especificar', 'Sin especificar')], default='Sin especificar', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='historicaljob',
            name='vacancies',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='category_level',
            field=models.CharField(choices=[('Mandos', 'Mandos'), ('Empleados', 'Empleados'), ('Técnicos', 'Técnicos'), ('Dirección', 'Dirección'), ('Sin especificar', 'Sin especificar')], default='Sin especificar', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='vacancies',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]