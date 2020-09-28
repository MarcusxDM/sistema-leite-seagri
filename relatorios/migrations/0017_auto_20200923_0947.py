# Generated by Django 3.0.7 on 2020-09-23 12:47

import cpf_field.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0016_remove_entidade_limit_beneficiarios'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beneficiario',
            name='id',
        ),
        migrations.AddField(
            model_name='beneficiario',
            name='cpf',
            field=cpf_field.models.CPFField(default='', max_length=14, primary_key=True, serialize=False, verbose_name='cpf'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='beneficiario',
            name='dap',
            field=models.CharField(max_length=50),
        ),
    ]
