from django.shortcuts import render, redirect
from django.core.mail import send_mail
from Entrenamiento.models import Firma, EntrenamientoPuestoNomenclatura, Entrenamiento
from Documentos.models import Plantilla, Documento, Historial
from Usuarios.models import Linea, Area, UsuarioPuesto, Puesto, PerfilUsuario
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import F, Value, CharField, Func, Q
from django.db.models.functions import Concat, Cast
from django.db.models.expressions import Case, When
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from django.db.models import F, Value, CharField, Case, When, IntegerField, ExpressionWrapper
from django.contrib import messages
from django.db import transaction
from urllib.parse import quote
from django.conf import settings
import re
from docx2pdf import convert
import os
from django.views.decorators.http import require_http_methods
from func.loading import aprobar_entrenamiento


# Create your views here.

#METODO PARA APROBAR EL ENTRENAMIENTO
def aprobar(request):
    template_name = "Entrenamiento/aprobar_entrenamiento.html"
    nombre_documento = doc_pendientes()
    entrenamiento_doc = None
    file_path = None

    if request.method == 'POST':
        action = request.POST.get('action')
        documento_seleccionado = request.POST.get('reviewInput', '')
        comment = request.POST.get('comment', '')

        if action == 'search' and documento_seleccionado:
            documentos = select_documento(documento_seleccionado)
            if documentos:
                id_archivo = documentos[0]['id']
                request.session['id_archivo'] = id_archivo  # Guardar en la sesión
                entrenamiento_doc = informaciondocs(id_archivo)
                linea_documento = entrenamiento_doc[0]['id_linea__nombre_linea']
                tipo_de_plantilla = entrenamiento_doc[0]['id_plantilla__nombre']
                documento_pdf = cambiar_la_extencion(documento_seleccionado)
                file_path = os.path.join(settings.MEDIA_URL, 'Control_de_documentos_pdfs', tipo_de_plantilla, linea_documento, documento_pdf)

        elif action == 'sign':
            id_archivo = request.session.get('id_archivo')
            if id_archivo:
                    # Lógica para firmar el documento
                    aprobar_entrenamiento(id_archivo, request.user.id)
                    messages.success(request, "Documento firmado exitosamente.")
                    request.session.pop('id_archivo', None)

                    return redirect('home')
            else:
                messages.error(request, "No existe un documento seleccionado para firmar.")
        


        elif action == 'reject':
            
            id_archivo = request.session.get('id_archivo')
            if id_archivo:
                documento = Documento.objects.get(id=id_archivo)
                usuario = User.objects.get(id=request.user.id)
                Documento.objects.filter(id=id_archivo).update(estado='ASIGNAR ENTRENAMIENTO')
                
                alta_historial = Historial.objects.create(
                        id_documento=documento,
                        id_responsable=usuario,
                        fecha=timezone.now(),
                        accion='ENTRENAMIENTO RECHAZADO'
                    )
                alta_historial.save()
                
                Entrenamiento.objects.filter(id_documento=id_archivo).update(estado='REALIZAR ENTRENAMIENTO', calificacion=None)
                messages.error(request, "El documento ha sido rechazado.")
                request.session.pop('id_archivo', None)

                return redirect('home')
            else:
                messages.error(request, "No existe un documento seleccionado para rechazar.")
        

    context = {
        'documentos': nombre_documento,
        'entrenamiento_info': entrenamiento_doc,
        'doc_pdf': file_path
    }
    
    return render(request, template_name, context)


#query para saber los pendientes que tiene le usuario de aprobar entrenamiento
def doc_pendientes():
    # Asegurándonos de que los Documentos están en el estado 'APROBADO'
   # Consulta ORM con condiciones
    documentos = Documento.objects.filter(
        estado='APROBAR ENTRENAMIENTO'
    ).select_related(
        'id_plantilla', 'id_linea'
    ).annotate(
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
    ).values(
        'id', 'Nombre_Documento', 'estado'
    )
    
    return documentos

#query de base de datos datos cuand se seleccione un dcouemnto
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
        autorizador=Concat(F('aprobador__first_name'), Value(' '), F('aprobador__last_name'))
    ).filter(
        nombre_documento=documento_seleccionado,
        estado='APROBAR ENTRENAMIENTO'
    ).values(
        'id', 'nombre_documento', 'id_linea__area__area', 'id_plantilla__nombre', 'revision_documento', 'autorizador'
    )
    
    return documentos

#query de base de datos para obtener resposable , Reviso, Autorizo, Nombre_Documento
def informaciondocs(id_documento):
    # Asegúrate de que 'Id_Documento' es una variable existente que contiene el ID deseado
    documentos_entrenamiento = Documento.objects.filter(id=id_documento).annotate(
        Responsable=Concat(F('id_responsable__first_name'), Value(' '), F('id_responsable__last_name'), output_field=CharField()),
        Reviso=Concat(F('revisador__first_name'), Value(' '), F('revisador__last_name'), output_field=CharField()),
        Autorizo=Concat(F('aprobador__first_name'), Value(' '), F('aprobador__last_name'), output_field=CharField()),
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
    ).values('Responsable', 'Reviso', 'Autorizo', 'Nombre_Documento', 'revision_documento', 'id_plantilla__nombre','id_linea__nombre_linea')
    
    return documentos_entrenamiento

@require_http_methods(["POST"])
def ajaxdocument_details(request):
    if request.method == 'POST':
        print(request.POST)
        nombre_documento = request.POST.get('nombre_documento', None)
        action = request.POST.get('action')

        
        if nombre_documento == '':

            print("si entre xddda")
            
            request.session.pop('documentos', None)
        
        if nombre_documento:
            print("el nombre de documento que tengo es: " , nombre_documento)
            documentos = select_documento(nombre_documento)
            documentos_list = list(documentos)  # Convertir QuerySet a lista
            request.session['documentos'] = documentos_list
            
            return JsonResponse(documentos_list, safe=False)
       

        
        return JsonResponse({'success': 200})
    
    
#metodo para cambiar la extension del documento    
def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre
