# Generated by Django 5.0.6 on 2024-07-21 22:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurante_app', '0005_pedido_pednumper'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedidodetalle',
            name='PedObs',
        ),
    ]