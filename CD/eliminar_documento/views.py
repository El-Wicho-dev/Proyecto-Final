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
#Eliminar Documento no terminado
def deletedoc(request):
    template_name = 'documentos/eliminar_documento.html'
    review_input_value = ''  # Inicializa la variable
    file_path = None  # Asegúrate de inicializar file_path para evitar referencias antes de asignación
    entrenamientos = None  # Asegúrate también de inicializar entrenamientos
    historial = None  # Asegúrate de inicializar historial

    if request.method == 'POST':
        review_input_value = request.POST.get('reviewInput', '')  # Captura el valor enviado
        action = request.POST.get('action')
        
        if action == 'search':
            documento = select_documento(review_input_value)
            if documento:
                id_documento = documento[0]['id']
                linea = documento[0]['id_linea__nombre_linea']
                plantilla = documento[0]['id_plantilla__nombre']
                
                print("linea del documento: ", linea, 'plantilla del documento', plantilla)

                entrenamientos = Entrenamiento.objects.filter(id_documento=id_documento).select_related('id_usuario').annotate(
                    nombre_completo=Concat(F('id_usuario__first_name'), Value(' '), F('id_usuario__last_name'))
                ).values('nombre_completo', 'calificacion', 'fecha')
                
                historial = Historial.objects.filter(id_documento=id_documento).select_related('id_responsable').annotate(
                    nombre_completo=Concat(F('id_responsable__first_name'), Value(' '), F('id_responsable__last_name'))
                ).values('nombre_completo', 'fecha', 'accion')
                
                documento_pdf = cambiar_la_extencion(review_input_value)
                
                if documento_pdf:
                    file_path = os.path.join(settings.MEDIA_URL, 'Control_de_documentos_pdfs', plantilla, linea, documento_pdf)

        elif action == 'reject':
            # Aquí va la lógica para eliminar documento
            messages.success(request,"SI ENTRE XD")
            #Firma.objects.filter(id_documento=id_documento).delete()

            # Eliminar registros en CD_Entrenamientos
            #Entrenamiento.objects.filter(id_documento=id_documento).delete()

            # Eliminar registros en CD_Historial_Aprobacion_Entrenamientos
            #Historial.objects.filter(id_documento=id_documento).delete()

            # Eliminar registros en CD_Liberar_Documento
            #Documento.objects.filter(id=id_documento).delete()
            
            #TENGO QUE HACER TAMBIEN ELIMNE EL DOCUMENTO RESPECTIVO
            
            return redirect("deletedoc")
            

    context = {
        'review_input_value': review_input_value,
        'pdf_url': file_path,
        'entrenamientos': entrenamientos,
        'historial_aprobacion': historial
    }
    
    return render(request, template_name, context)



def autocomplete_nomenclatura(request):
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
    ).filter(estado='APROBADO')

    nomenclaturas = list(documentos.values_list('nomenclatura', flat=True))
    return JsonResponse(nomenclaturas, safe=False)



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



def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre
