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
def aprobar(request):
    template_name = "Entrenamiento/aprobar_entrenamiento.html"
    
    nombre_documento = doc_pendientes()
    
    action = request.POST.get('action')
    comment = request.POST.get('comment', '')
    print(request.POST)

    # Obtén los documentos seleccionados de la sesión
    documento_seleccionado = request.session.get('documentos', [])
    
    # Verifica si la lista está vacía y elimina la clave si es necesario
    if not documento_seleccionado:
        request.session.pop('documentos', None)
        # No redirigir aquí, en su lugar mostrar un mensaje y continuar
        documento_seleccionado = []  # Asegura que la lista esté vacía

    # Asume que siempre hay un documento en la lista seleccionada y toma el primero si hay alguno
    if documento_seleccionado:
        id_archivo = documento_seleccionado[0]['id']
        print("id documento:", id_archivo)

        # Obtén la información del entrenamiento
        entrenamientos = Entrenamiento.objects.filter(id_documento=id_archivo).annotate(
            nombre_completo=Concat(
                F('id_usuario__first_name'),
                Value(' '),
                F('id_usuario__last_name'),
                output_field=CharField()
            )
        ).values(
            'nombre_completo', 'calificacion', 'fecha'
        )

        for entrenamiento in entrenamientos:
            print(entrenamiento['nombre_completo'])

        # Obtén la información del documento
        entrenamiento_doc = informaciondocs(id_archivo)

        # Variables para almacenar la información del documento
        linea_documento = ""
        nombre_doc = ""
        tipo_de_plantilla = ""

        # Iterar sobre el queryset y imprimir cada campo anotado
        for documento in entrenamiento_doc:
            print("Responsable:", documento['Responsable'])
            print("Reviso:", documento['Reviso'])
            print("Autorizo:", documento['Autorizo'])
            print("Revison del documento:", documento['revision_documento'])
            print("Linea del documento:", documento['id_linea__nombre_linea'])
            linea_documento = documento['id_linea__nombre_linea']
            nombre_doc = documento['Nombre_Documento']
            print("Nombre del Documento:", nombre_doc)
            print("tipo de Documento:", documento['id_plantilla__nombre'])
            tipo_de_plantilla = documento['id_plantilla__nombre']

        # Cambiar la extensión del documento
        documento_pdf = cambiar_la_extencion(nombre_doc)

        # Construir la ruta del archivo PDF solo si hay documentos disponibles
        if nombre_doc:
            file_path = os.path.join(settings.MEDIA_URL, 'Control_de_documentos_pdfs', tipo_de_plantilla, linea_documento, documento_pdf)
        else:
            file_path = None  # No hay documento disponible
        
        print('tu ruta', file_path)

        if action == 'sign':
            print("entre al boton de firmar")
            
            if not nombre_documento:
                messages.error(request, "No hay documentos seleccionados.")
                return render(request, template_name, {
                    'documentos': nombre_documento,
                    'entrenamiento_info': [],
                    'doc_pdf': None
                })
                    
            aprobar_entrenamiento(id_archivo, nombre_doc, request.user.id)
            messages.success(request, "Documento firmado exitosamente.")
            return redirect('home')

        elif action == 'reject':
            print("entre al boton de rechazar")
            
            if not nombre_documento:
                messages.error(request, "No hay documentos seleccionados.")
                return render(request, template_name, {
                    'documentos': nombre_documento,
                    'entrenamiento_info': [],
                    'doc_pdf': None
                })
            
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
            return redirect('home')
    else:
        # No hay documentos seleccionados
        entrenamientos = []
        entrenamiento_doc = []
        file_path = None

    context = {
        'documentos': nombre_documento,
        'entrenamiento_info': entrenamiento_doc,
        'doc_pdf': file_path  # Solo incluye la ruta del PDF si hay documentos
    }
        
    return render(request, template_name, context)






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

def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre
