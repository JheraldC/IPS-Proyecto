# Generated by Django 5.0.6 on 2024-07-21 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurante_app', '0004_alter_pedido_pedobs'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='PedNumPer',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
