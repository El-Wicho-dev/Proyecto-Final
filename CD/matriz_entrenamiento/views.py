from django.shortcuts import render
from func.loading import cargar_matriz
from django.db.models import F, Value, CharField,Case,When
from django.db.models.functions import Concat, Cast
from Entrenamiento.models import Entrenamiento,EntrenamientoPuestoNomenclatura,Firma
from Documentos.models  import Documento,Plantilla
from Usuarios.models import UnidadNegocio,Puesto,UsuarioPuesto,PerfilUsuario
# Create your views here.


def matriz(request):
    template = 'Entrenamiento/matriz_de_entrenamiento.html'
    
    data = cargar_matriz()

   
    context = {
       'columns': data['columns'],
       'rows': data['rows'],
       'total_porcentaje': data['total_porcentaje'],  # Pasar el porcentaje total al contexto
    }
    return render(request,template,context)


def nomenclatura():

# Build the queryset
    queryset = Documento.objects.filter(
        id_plantilla__nombre__in=['PROCEDIMIENTO', 'MANUAL'],  # Match names 'PROCEDIMIENTO' or 'MANUAL'
        estado='APROBADO'  # Match state 'APROBADO'
    ).annotate(
        plantilla_codigo=F('id_plantilla__codigo'),  # Get 'codigo' from related 'Plantilla' model
        linea_codigo=F('id_linea__codigo_linea'),  # Get 'codigo_linea' from related 'Linea' model
        nomenclatura=Concat(
            F('id_plantilla__codigo'), Value('-'), F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo='00', then=Value('00')),
                When(consecutivo__lt='10', then=Concat(Value('0'), Cast(F('consecutivo'), CharField()))),  # Handle padding for 'consecutivo' less than 10
                default=Cast(F('consecutivo'), CharField()),  # Default case for 'consecutivo'
                output_field=CharField()
            )
        )
    ).filter(
        nomenclatura__in=EntrenamientoPuestoNomenclatura.objects.values_list('nomenclatura', flat=True)  # Check 'nomenclatura' in related 'EntrenamientoPuestoNomenclatura'
    ).distinct().order_by('nomenclatura').values('nomenclatura')  # Distinct and order by 'nomenclatura', returning only 'nomenclatura'
    
    for query in queryset:
        print(query.nomenclatura)



