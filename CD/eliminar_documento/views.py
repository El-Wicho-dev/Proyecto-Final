from django.shortcuts import render
from Documentos.views import documentosquery
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.db.models import Case, When, Value, CharField, F
from django.db.models.functions import Cast,Concat
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
import os
import time
from Documentos.models import Plantilla,Documento,DocumentoBloqueado,Historial
from Usuarios.models import UsuarioPuesto
from Entrenamiento.models import Entrenamiento,EntrenamientoPuestoNomenclatura,Firma



# Create your views here.
#METODO PARA ELIMINAR UN DOCUMENTO SELCCIOANDO DE USUARIO EN LA BASE DE DATOS Y RENDERIZA EL FORMULARIO
def deletedoc(request):
    template_name = 'documentos/eliminar_documento.html'
    nomenclatura = ''  # Inicializa la variable
    file_path = None  # Asegúrate de inicializar file_path para evitar referencias antes de asignación
    entrenamientos = None  # Asegúrate también de inicializar entrenamientos
    historial = None  # Asegúrate de inicializar historial
    id_documento = None

    if request.method == 'POST':
        nomenclatura = request.POST.get('nomenclatura_text', '')  # Captura el valor de nomenclatura
        action = request.POST.get('action')
        print(request.POST)
        
        documento = select_documento(nomenclatura)
        
        if documento:
            id_documento = documento[0]['id']
            linea = documento[0]['id_linea__nombre_linea']
            plantilla = documento[0]['id_plantilla__nombre']
            
            #print("linea del documento: ", linea, 'plantilla del documento', plantilla)

            entrenamientos = Entrenamiento.objects.filter(id_documento=id_documento).select_related('id_usuario').annotate(
                nombre_completo=Concat(F('id_usuario__first_name'), Value(' '), F('id_usuario__last_name'))
            ).values('nombre_completo', 'calificacion', 'fecha')
            
            historial = Historial.objects.filter(id_documento=id_documento).select_related('id_responsable').annotate(
                nombre_completo=Concat(F('id_responsable__first_name'), Value(' '), F('id_responsable__last_name'))
            ).values('nombre_completo', 'fecha', 'accion')
            
            documento_pdf = cambiar_la_extencion(nomenclatura)
            
            print(documento_pdf)
            
            if documento_pdf:
                print("entre")
                file_path = os.path.join(settings.MEDIA_URL, 'Control_de_documentos_pdfs', plantilla, linea, documento_pdf)
                print(file_path)
        
        
        if action == 'reject':
            # Aquí va la lógica para eliminar documento
                id_nomenclatura = request.POST.get('nomenclatura', '')  # Captura el valor de nomenclatura
                documento_xd = select_documento(id_nomenclatura)
                
                if documento_xd:
                    
                    
                    id_documento_delete = documento_xd[0]['id']
                    
                    print('TU ID PARA ELIMINAR ES: ',id_documento_delete)
                    
                    
                     #print(id_documento)
                    #FSFirma.objects.filter(id_documento=id_documento).delete()

                    #Eliminar registros en CD_Entrenamientos
                    #Entrenamiento.objects.filter(id_documento=id_documento).delete()

                    # Eliminar registros en CD_Historial_Aprobacion_Entrenamientos
                    #Historial.objects.filter(id_documento=id_documento).delete()

                    # Eliminar registros en CD_Liberar_Documento
                    #Documento.objects.filter(id=id_documento).delete()
                    
                    #TENGO QUE HACER TAMBIEN ELIMNE EL DOCUMENTO RESPECTIVO

                    messages.success(request,"El documento ha sido desbloqueado de manera exitosa")
                    
                    return redirect("deletedoc")
                
            
            

                #print(id_documento)
                #Firma.objects.filter(id_documento=id_documento).delete()

                # Eliminar registros en CD_Entrenamientos
                #Entrenamiento.objects.filter(id_documento=id_documento).delete()

                # Eliminar registros en CD_Historial_Aprobacion_Entrenamientos
                #Historial.objects.filter(id_documento=id_documento).delete()

                # Eliminar registros en CD_Liberar_Documento
                #Documento.objects.filter(id=id_documento).delete()
                
                #TENGO QUE HACER TAMBIEN ELIMNE EL DOCUMENTO RESPECTIVO
                
            
                
            

    context = {
        'nomenclatura_text': nomenclatura,
        'pdf_url': file_path,
        'entrenamientos': entrenamientos,
        'historial_aprobacion': historial
    }
    print(context)
    
    return render(request, template_name, context)


#QUERY EN LA CUAL AUTOCOMPLETA EL NOMBRE DEL DOCUMENTO DE AJAX CON RESPECTO  LO QUE INGRESE EL SUUARIO 
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


#AJAX OBTIENE LOS DATOS CON RESPECTOS AL DOCUMENTO SELCCIOANDO DEL QUERY
def select_documento(documento_seleccionado):
    documentos = Documento.objects.annotate(
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
            output_field=CharField()
        ),
    ).filter(
        nombre_documento=documento_seleccionado,
        estado='APROBADO'
    ).values(
        'id','id_linea__area__area', 'id_plantilla__nombre','id_linea__nombre_linea'
    )
    
    return documentos


#Metodo para cambiar extension del documento
def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre
