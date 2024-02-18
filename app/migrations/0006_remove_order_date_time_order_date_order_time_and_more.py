# Generated by Django 4.2.10 on 2024-02-18 14:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_customcake_berries_alter_customcake_decor_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='date_time',
        ),
        migrations.AddField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата доставки'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='time',
            field=models.CharField(default=-4, max_length=50, verbose_name='Время доставки'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderbasecake',
            name='amount',
            field=models.IntegerField(default=1, verbose_name='Количество тортов в заказе'),
        ),
    ]