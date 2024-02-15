# Generated by Django 4.2.10 on 2024-02-15 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_order_customcake_berries_customcake_decor_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basecake',
            options={'ordering': ['title'], 'verbose_name': 'Торт из меню', 'verbose_name_plural': 'Торты из меню'},
        ),
        migrations.AlterModelOptions(
            name='customcake',
            options={'verbose_name': 'Кастомный торт', 'verbose_name_plural': 'Кастомные торты'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='customcake',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='custom_cakes', to='app.client', verbose_name='Клиент'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customcake',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_cakes', to='app.order', verbose_name='Заказ'),
        ),
    ]
