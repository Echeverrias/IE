# Generated by Django 2.2.2 on 2019-11-30 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20191121_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='pid',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
