# Generated by Django 3.0.7 on 2020-08-14 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0006_auto_20200814_1805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cooperativa',
            name='cod_ibge',
        ),
    ]
