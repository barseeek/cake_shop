# Generated by Django 4.2.10 on 2024-02-18 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_basecake_options_alter_customcake_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advertising',
            options={'verbose_name': 'Реклама', 'verbose_name_plural': 'Реклама'},
        ),
        migrations.AlterModelOptions(
            name='orderbasecake',
            options={'verbose_name': 'Торт из меню в заказе', 'verbose_name_plural': 'Торты из меню в заказе'},
        ),
        migrations.AlterField(
            model_name='advertising',
            name='responses',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Количество откликов'),
        ),
        migrations.AlterField(
            model_name='advertising',
            name='url',
            field=models.URLField(blank=True, verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='client',
            name='username',
            field=models.CharField(max_length=100, unique=True, verbose_name='Имя пользователя в Telegram'),
        ),
        migrations.AlterField(
            model_name='order',
            name='base_cakes',
            field=models.ManyToManyField(blank=True, related_name='orders', through='app.OrderBaseCake', to='app.basecake', verbose_name='Торты из меню'),
        ),
    ]
