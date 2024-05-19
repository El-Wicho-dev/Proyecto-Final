from django.shortcuts import render
from Entrenamiento.models import Firma,EntrenamientoPuestoNomenclatura,Entrenamiento
from Documentos.models import Plantilla,Documento,Historial
from Usuarios.models  import Linea,Area,UsuarioPuesto,Puesto
from django.db.models import F, Value , CharField,Func,Q,Case,When
from django.db.models.functions import Concat,Cast,Coalesce
from django.http import HttpResponse,JsonResponse


def logbook(request):
    template = 'documentos/bitacora.html'
    
    areas = Area.objects.all().values_list('area', flat=True)
    plantillas = Plantilla.objects.all().values_list('nombre', flat=True)
    documento_estado = Documento.objects.all().values_list('estado', flat=True).distinct()

    # Preparar la query de documentos, no necesitas convertir a listas aquí
    Documentos = Documento.objects.select_related(
    'id_plantilla', 'id_linea', 'id_responsable', 'revisador', 'aprobador'
    ).annotate(
        nombre_del_documento=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo='00', then=Value('00')),
                When(consecutivo__lt=10, then=Concat(Value('0'), Cast('consecutivo', CharField()))),
                default=Cast('consecutivo', CharField())
            ),
            Value(' REV. '), F('revision_documento'), Value(' '), F('nombre'),
            output_field=CharField()
        ),
        plantilla_nombre=F('id_plantilla__nombre'),
        linea_nombre=F('id_linea__nombre_linea'),
        area=F('id_linea__area__area'),
        nombre_responsable=Concat('id_responsable__first_name', Value(' '), 'id_responsable__last_name'),
        nombre_revisor=Concat('revisador__first_name', Value(' '), 'revisador__last_name'),
        nombre_aprobador=Concat('aprobador__first_name', Value(' '), 'aprobador__last_name'),
        fecha_con_texto=Coalesce(
                Cast('fecha_finalizacion', CharField()),  # Asegurando que la fecha sea tratada como texto
                Value('Sin Finalizar'),  # Valor alternativo si la fecha es nula
                output_field=CharField()  # Salida como texto
            )    
    ).order_by('nombre_del_documento')

    context = {
        'areas': areas,
        'plantillas': plantillas,
        'estados': documento_estado,
        'documentos': Documentos
    }
    
    return render(request, template, context)