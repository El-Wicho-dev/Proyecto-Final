# Generated by Django 5.0.2 on 2024-03-20 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0002_alter_puesto_por_unidad_negocio_alter_puesto_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='estado',
            field=models.CharField(default='ACTIVO', max_length=10),
        ),
    ]