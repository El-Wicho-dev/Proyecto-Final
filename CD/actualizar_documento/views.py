from django.shortcuts import render
import os
from django.http import HttpResponse,JsonResponse
from Documentos.models import Plantilla,Documento,DocumentoBloqueado,Historial
from django.db.models import Case, When, Value, CharField, F
from django.db.models.functions import Cast,Concat
# Create your views here.
def update_document(request):
    template = 'documentos/actualizar_documento.html'
    
    
    
    context = {
        
    }
    
    return render(request,template,context)




def autocomplete_nomenclatura(request):
    searchTerm = request.GET.get('searchTerm', '')  # Obtiene el término de búsqueda de la petición GET
    documentos = Documento.objects.annotate(
        nomenclatura=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo='00', then=Value('00')),
                When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'))),
                default=F('consecutivo'),
                output_field=CharField()
            ),
            Value(' REV. '), F('revision_documento'), Value(' '), F('nombre'),
            output_field=CharField()
        )
    ).filter(nomenclatura__icontains=searchTerm, estado='APROBADO')  # Filtra por searchTerm y estado

    nomenclaturas = list(documentos.values('id', 'nomenclatura'))  # Obtiene 'id' y 'nomenclatura'
    results = [{'id': n['id'], 'text': n['nomenclatura']} for n in nomenclaturas]
    return JsonResponse({'results': results})  # Ajusta la estructura de la respuesta para Select2



def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre
