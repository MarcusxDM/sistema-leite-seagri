# Generated by Django 3.0.7 on 2020-08-14 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0003_usuario_seagri_bool'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='telefone',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]
