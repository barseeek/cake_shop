# Generated by Django 4.2.10 on 2024-02-19 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_cake_remove_customcake_client_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cake',
            name='title',
            field=models.CharField(default='Пользовательский торт', max_length=100, verbose_name='Название'),
        ),
    ]