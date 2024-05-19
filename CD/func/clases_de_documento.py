from Documentos.models import Documento, Plantilla
from Usuarios.models import Linea,Area
from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Cast,Concat
from django.contrib import messages
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings



def nomenclatura(nombre):
    if nombre is None:
        raise ValueError("El nombre del documento no puede ser None.")
    
    print("hola si entro")
    # Dividir en partes principales
    partes = nombre.split()
    
    # Obtener no_documento y no_linea
    no_documento, no_linea = partes[0].split('-')
    
    # Obtener el consecutivo
    consecutivo = partes[1]
    
    # Verificar y extraer la revisión
    if partes[2] == "REV.":
        revision = partes[3]
        # Unir el resto del nombre del documento
        nombre_del_documento = ' '.join(partes[4:])
    else:
        revision = None
        nombre_del_documento = ' '.join(partes[2:])
    
    return no_documento, no_linea, consecutivo, revision, nombre_del_documento


def get_ruta_actual(id_documento):
    documento = Documento.objects.select_related('id_plantilla', 'id_linea', 'id_linea__area').get(pk=id_documento)
    plantilla = documento.id_plantilla.nombre
    linea = documento.id_linea.nombre_linea
    tipo = documento.id_plantilla.tipo_de_area
    area = documento.id_linea.area.area

    ruta = Concat(
        Value(documento.id_plantilla.ruta_principal + '\\'),
        Case(
            When(tipo_de_area='1', then=Concat(
                Value('Clientes\\'),
                F('id_linea__area__area'),
                Value('\\')
            )),
            default=Value('')
        ),
        F('id_linea__nombre_linea'),
        Value('\\'),
        F('nombre')
    )
    return ruta.annotate(ruta_completa=F('ruta_completa')).first().ruta_completa


def get_ruta_obsoleta(id_documento):
    documento = Documento.objects.select_related('id_plantilla', 'id_linea', 'id_linea__area').get(pk=id_documento)
    plantilla, linea, _, rev_anterior, nombre_doc = nomenclatura(documento.nombre)
    tipo = documento.id_plantilla.tipo_de_area
    area = documento.id_linea.area.area
    nomenclatura_anterior = f"{plantilla}-{linea} {documento.consecutivo} REV.{rev_anterior} {nombre_doc}"

    if tipo == '2' or (tipo == '4' and area == 'Departamento'):
        ruta_obsoleta_destino = f"\\{plantilla}\\{linea}\\OBSOLETO\\{nomenclatura_anterior}"
        ruta_obsoleta_actual = f"\\{plantilla}\\{linea}\\{nomenclatura_anterior}"
    elif tipo in ['1', '4']:
        ruta_obsoleta_destino = f"\\{plantilla}\\Clientes\\{area}\\{linea}\\OBSOLETO\\{nomenclatura_anterior}"
        ruta_obsoleta_actual = f"\\{plantilla}\\Clientes\\{area}\\{linea}\\{nomenclatura_anterior}"
    else:
        ruta_obsoleta_destino = f"\\Plantillas\\OBSOLETO\\{nomenclatura_anterior}"
        ruta_obsoleta_actual = f"\\Plantillas\\{nomenclatura_anterior}"

    return ruta_obsoleta_actual, ruta_obsoleta_destino



def buscar_nomenclatura(request, nomenclatura):
    documento = get_object_or_404(Documento, nomenclatura=nomenclatura, estado='APROBADO')
    ruta_pdf = os.path.join(settings.RUTA_PRINCIPAL, get_ruta_actual(documento.id) + '.pdf')

    if os.path.exists(ruta_pdf):
        try:
            return HttpResponse(open(ruta_pdf, 'rb'), content_type='application/pdf')
        except Exception as ex:
            # Aquí manejar la excepción adecuadamente
            return HttpResponse(f"Error al abrir el documento: {str(ex)}", status=500)
    else:
        # Log de error no encontrado
        return HttpResponse("Documento no encontrado en la ruta esperada.", status=404)
