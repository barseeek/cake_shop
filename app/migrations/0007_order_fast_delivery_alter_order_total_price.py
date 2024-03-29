# Generated by Django 4.2.10 on 2024-02-18 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_order_date_time_order_date_order_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fast_delivery',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.FloatField(blank=True, null=True, verbose_name='Конечная цена'),
        ),
    ]
