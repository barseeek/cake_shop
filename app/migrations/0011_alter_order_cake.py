# Generated by Django 4.2.10 on 2024-02-19 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_cake_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cake',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to='app.cake', verbose_name='Торт'),
        ),
    ]
