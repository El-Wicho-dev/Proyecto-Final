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
    try:
        document = Documento.objects.filter(id=id_documento).annotate(
            Nombre_Documento=Concat(
                F('id_plantilla__codigo'), Value('-'),
                F('id_linea__codigo_linea'), Value(' '),
                Case(
                    When(consecutivo='00', then=Value('00')),
                    When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'), output_field=CharField())),
                    default=F('consecutivo'),
                    output_field=CharField()
                ),
                Value(' REV. '),
                F('revision_documento'), Value(' '),
                F('nombre'),
                output_field=CharField()
            )
        ).select_related('id_plantilla', 'id_linea').first()

        if not document:
            raise ValueError("Documento no encontrado.")

        # Calcula la revisión anterior
        rev = int(document.revision_documento)
        rev_anterior = f"{rev - 1:02d}"
        nombre_archivo = document.Nombre_Documento
        no_documento, no_linea, consecutivo, revision, nombre_del_documento = nomenclatura(nombre_archivo)
        nomenclatura_anterior = f"{no_documento}-{no_linea} {consecutivo} REV. {rev_anterior} {nombre_del_documento}"

        base_path = f"{document.id_plantilla.nombre}/{document.id_linea.nombre_linea}"
        ruta_obsoleta_destino = f"/{base_path}/OBSOLETO/{nomenclatura_anterior}"
        ruta_obsoleta_actual = f"/{base_path}/{nomenclatura_anterior}"

        print(ruta_obsoleta_actual, ruta_obsoleta_destino)
        return ruta_obsoleta_actual, ruta_obsoleta_destino,base_path

    except Exception as e:
        print(f"Error al obtener la ruta obsoleta: {e}")
        return None, None



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
