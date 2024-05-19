# Generated by Django 5.0.2 on 2024-04-26 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documentos', '0012_alter_plantilla_archivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentobloqueado',
            name='fecha',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='documentobloqueado',
            name='intentos_descarga',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='plantilla',
            name='nombre',
            field=models.CharField(choices=[('FORMATOS', 'FORMATOS'), ('GUIAS', 'GUIAS'), ('PROCEDIMIENTO', 'PROCEDIMIENTO'), ('AYUDA VISUAL', 'AYUDA VISUAL'), ('PLANTILLA', 'PLANTILLA'), ('DIAGRAMA DE FLUJO', 'DIAGRAMA DE FLUJO')], max_length=100),
        ),
    ]