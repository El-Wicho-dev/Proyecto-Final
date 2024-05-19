from django.http import HttpResponse,JsonResponse
from docx import Document
from Documentos.models import DocumentoBloqueado
from docx.shared import Inches
from django.db import transaction
from django.shortcuts import render
from datetime import datetime
import os


class ConfiguracionDocumento:
    def __init__(self, ruta_word):
        self.ruta_word = ruta_word
        
def insertar_referencia_imagen(request, codigo, ruta_imagen):
    try:
        DocumentoBloqueado.objects.create(
            nomenclatura=codigo,
            fecha=datetime.now(),
            id_responsable=request.user,
            estado='Activo',
            codigo_identificacion=ruta_imagen,
            intentos_descarga=0
        )
        return JsonResponse({'success': True, 'message': 'Imagen referencia guardada con éxito'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# Asegúrate de conectar esta vista a una URL en urls.py



def insertar_referencia_imagen(request, codigo, ruta_imagen):
        doc_bloqueado = DocumentoBloqueado.objects.create(
            nomenclatura=codigo,
            fecha=datetime.now(),
            id_responsable=request.user,
            estado='Activo',
            codigo_identificacion=ruta_imagen,
            intentos_descarga=0
        )
        doc_bloqueado.save()

    
    
def quitar_sellos(request, ruta_word):
    # Parse the file name to get document nomenclature
    nombre = ruta_word.split('/')[-1]
    no_documento, no_linea, consecutivo, rev, nombre_del_documento = DocumentoBloqueado.nomenclatura(nombre)
    nomenclatura = f"{no_documento}-{no_linea} {consecutivo}"

    # Retrieve the identifier code using Django ORM
    try:
        documento_bloqueado = DocumentoBloqueado.objects.get(nomenclatura=nomenclatura)
        codigo_identificador = documento_bloqueado.codigo_identificacion
    except DocumentoBloqueado.DoesNotExist:
        return render(request, 'error.html', {'message': 'Documento bloqueado no encontrado.'})

    # Process Word document
    try:
        doc = Document(ruta_word)
        for section in doc.sections:
            header = section.header
            if header.is_linked_to_previous:
                continue
            
            for shape in header.shapes:
                if shape.shape_type == 'picture':
                    if shape.name in ["CI9449-ILEPP7677-ENTRENAMIENTO", "CI9449-ILEPP7677-DOCUMENTOS", codigo_identificador]:
                        shape.delete()

        # Save the modified document
        doc.save(ruta_word.replace('.docx', '_modified.docx'))

    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})

    # Clean up database entry
    with transaction.atomic():
        DocumentoBloqueado.objects.filter(nomenclatura=nomenclatura).delete()

    return render(request, 'success.html', {'message': 'Sellos quitados correctamente.'})