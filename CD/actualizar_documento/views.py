from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from Documentos.models import Documento,Plantilla
from Usuarios.models import Linea
from django.db.models import Case, When, Value, CharField, F
from django.core.files.storage import default_storage
from django.db.models.functions import Concat
from django.contrib import messages
from django.conf import settings
from func.clases_de_documento import nomenclatura 
import os

# Vista para actualizar documento
def update_document(request):
    template = 'documentos/actualizar_documento.html'
    if request.method == 'POST':
        documento_editable = request.FILES.get('documentoEditable')
        documento_pdf = request.FILES.get('documentoPDF')
        idnomenclatura = request.POST.get('nomenclatura', '')
        
        documentos = informaciondocs(idnomenclatura)
        
        if documentos:
            nombre_de_documento = documentos.nombre_documento
            
            no_documento, no_linea, consecutivo, revision, nombre_del_documento = nomenclatura(nombre_de_documento)
            
            Lineas = Linea.objects.get(codigo_linea=no_linea)
            nombre_linea = Lineas.nombre_linea
            
            Plantillas = Plantilla.objects.get(codigo=no_documento)
            tipo_de_plantilla = Plantillas.nombre
            
            base_nombre_documento = nombre_de_documento.rsplit('.', 1)[0]  # Quitar la extensión actual
            
            ruta_Editable_remplazo = f'{settings.MEDIA_ROOT_EDITABLE}/{tipo_de_plantilla}/{nombre_linea}/{base_nombre_documento}.docx'
            ruta_pdf_remplazo = f'{settings.MEDIA_ROOT_PDF}/{tipo_de_plantilla}/{nombre_linea}/{base_nombre_documento}.pdf'
            
            if documento_editable:
                # Borrar el archivo actual si existe
                if default_storage.exists(ruta_Editable_remplazo):
                    default_storage.delete(ruta_Editable_remplazo)
                # Guardar el nuevo archivo
                default_storage.save(ruta_Editable_remplazo, documento_editable)

            if documento_pdf:
                # Borrar el archivo actual si existe
                if default_storage.exists(ruta_pdf_remplazo):
                    default_storage.delete(ruta_pdf_remplazo)
                # Guardar el nuevo archivo
                default_storage.save(ruta_pdf_remplazo, documento_pdf)
                
            
            messages.success(request,"Se actualizado el archivo correctamente")
            
            return redirect('home')
        else:
            return redirect('update_document')
    else:
        context = {}
        return render(request, template, context)


# Vista para autocompletar nomenclatura
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

# Función para cambiar la extensión del nombre del documento
def cambiar_la_extencion(nombre_documento):
    base_nombre, ext = os.path.splitext(nombre_documento)
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        return f"{base_nombre}.pdf"
    return nombre_documento  # Devuelve el nombre original si no es .docx o .doc


#query parta bootener los nombres de del documentos 
def informaciondocs(id_documento):
    documento = (
        Documento.objects
        .filter(id=id_documento)
        .annotate(
            Responsable=Concat(F('id_responsable__first_name'), Value(' '), F('id_responsable__last_name'), output_field=CharField()),
            Reviso=Concat(F('revisador__first_name'), Value(' '), F('revisador__last_name'), output_field=CharField()),
            Autorizo=Concat(F('aprobador__first_name'), Value(' '), F('aprobador__last_name'), output_field=CharField()),
            nombre_documento=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo='00', then=Value('00')),
                When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'))),
                default=F('consecutivo'),
                output_field=CharField(),
            ),
            Value(' REV. '),
            F('revision_documento'), Value(' '),
            F('nombre'),
            output_field=CharField()),
            Rev_Documento=F('revision_documento'),
            Rev_Plantilla=F('revision_de_plantilla'),
            Plantilla_Nombre=F('id_plantilla__nombre'),
            Area=F('id_linea__area__area'),
            Linea=F('id_linea__nombre_linea'),
            Id_Firma_Reviso=F('firmas__id'),
            Id_Firma_Autorizo=F('firmas__id')
        )
        .select_related('id_responsable', 'revisador', 'aprobador', 'id_linea', 'id_plantilla')
        .first()
    )

    # Para obtener los resultados, accede a los campos anotados
    #if documento:
        #print("Responsable:", documento.Responsable)
        #print("Reviso:", documento.Reviso)
        #print("Autorizo:", documento.Autorizo)
        #print("Nombre Documento:", documento.Nombre_Documento)
        #print("Rev Documento:", documento.Rev_Documento)
        #print("Rev Plantilla:", documento.Rev_Plantilla)
        #print("Nombre Plantilla:", documento.Plantilla_Nombre)
        #print("Area:", documento.Area)
        #print("Linea:", documento.Linea)
        #print("ID Firma Reviso:", documento.Id_Firma_Reviso)
        #print("ID Firma Autorizo:", documento.Id_Firma_Autorizo)
        #print("Tipo de Area:", documento.id_plantilla.tipo_de_area)

    return documento
