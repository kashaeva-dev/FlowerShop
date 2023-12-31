# Generated by Django 4.2.4 on 2023-08-22 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopbot', '0003_rename_lenght_flower_length_alter_flower_genus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flower',
            name='genus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shopbot.genus', verbose_name='Род растения'),
        ),
        migrations.AlterField(
            model_name='greenerycomposition',
            name='quantity',
            field=models.FloatField(verbose_name='Количество'),
        ),
    ]
