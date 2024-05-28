from django.shortcuts import render,get_object_or_404,redirect
from Documentos.models import DocumentoBloqueado
from django.db.models import F, Value, CharField,ExpressionWrapper,fields,IntegerField
from django.db.models.functions import Concat,Now,ExtractDay
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

# Create your views here.

#Metodo para bloquear el documento  
def blockdoc(request):
    template = 'documentos/bloquear_documento.html'
    
    #query que muestre los documentos que esta en estado de En edición
    documentos_bloqueados = DocumentoBloqueado.objects.filter(estado='En edición').annotate(
        nombre=Concat(F('id_responsable__first_name'), Value(' '), F('id_responsable__last_name'), output_field=CharField())
    ).values(
        'nomenclatura',
        'nombre',
        'fecha',
        'intentos_descarga'
    )

    # Convert date to days
    today = timezone.now().date()
    documentos_bloqueados_list = list(documentos_bloqueados)
    for documento in documentos_bloqueados_list:
        fecha = documento['fecha']
        
        dias_transcurridos = (today - fecha).days
        documento['dias_transcurridos_in_days'] = dias_transcurridos
        
    context = {
        'documentos_bloqueados': documentos_bloqueados_list
    }
    
    print("Context:", context)

    
    return render(request,template,context)

#Metod ono elimina el document obloqueado relacionado con la nomenclatura seleccioando por el usuario
def ajax_nomnenclatura(request,nomenclatura):
    if request.method == 'POST':
        print(nomenclatura)
        documento = get_object_or_404(DocumentoBloqueado, nomenclatura=nomenclatura, estado='En edición')
        documento.delete()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error'}, status=400)
    
    