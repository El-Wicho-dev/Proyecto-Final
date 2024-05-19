# Generated by Django 5.0.2 on 2024-04-07 07:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documentos', '0007_remove_formatospermitidos_id_documento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documento',
            old_name='revision',
            new_name='revisador',
        ),
        migrations.AlterField(
            model_name='documento',
            name='fecha_finalizacion',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='documento',
            name='fecha_inicio',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='formatospermitidos',
            name='Extencion',
            field=models.CharField(choices=[('.ppt', '.ppt (PowerPoint)'), ('.pptx', '.pptx (PowerPoint)'), ('.xls', '.xls (Excel)'), ('.xlsx', '.xlsx (Excel)'), ('.doc', '.doc (Word)'), ('.docx', '.docx (Word)'), ('.pdf', '.pdf (PDF)')], max_length=50),
        ),
    ]