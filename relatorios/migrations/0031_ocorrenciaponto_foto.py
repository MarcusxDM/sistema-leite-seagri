# Generated by Django 3.0.7 on 2020-12-15 13:53

from django.db import migrations, models
import relatorios.models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0030_delete_ocorrenciacoop'),
    ]

    operations = [
        migrations.AddField(
            model_name='ocorrenciaponto',
            name='foto',
            field=models.ImageField(null=True, upload_to=relatorios.models.path_and_rename),
        ),
    ]
