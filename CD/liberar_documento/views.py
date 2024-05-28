import subprocess
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
from func.loading import aprobar_entrenamiento,cargar_documento


#Metodo para liberar el documento final
def liberar(request):
    template = 'documentos/liberar_documento.html'
    nombre_documento = doc_pendientes()
    info = None
    file_path = None

    if request.method == 'POST':
        action = request.POST.get('action')
        documento_nombre = request.POST.get('reviewInput', None)

        if action == 'search' and documento_nombre:
            documentos = select_documento(documento_nombre)
            if documentos.exists():
                id_archivo = documentos[0]['id']
                name_document = documentos[0]['nombre_documento']
                info = informaciondocs(id_archivo)
                if info:
                    linea_documento = info.Linea
                    tipo_de_plantilla = info.Plantilla_Nombre
                    documento_pdf = cambiar_la_extencion(name_document)
                    file_path = os.path.join(settings.MEDIA_URL, 'Control_de_documentos_pdfs', tipo_de_plantilla, linea_documento, documento_pdf)
                    # Guardar en sesión el id del documento seleccionado
                    request.session['id_archivo'] = id_archivo
                    request.session['linea_documento'] = linea_documento
                    request.session['tipo_de_plantilla'] = tipo_de_plantilla
                    request.session['name_document'] = name_document


                    print('id archivo', id_archivo)
            else:
                messages.error(request, "Documento no encontrado.")

        elif action == 'sign':
            id_archivo = request.session.get('id_archivo')
            name_document = request.session.get('name_document')
            tipo_de_plantilla = request.session.get('tipo_de_plantilla')
            if id_archivo:
                # Lógica para firmar el documento
                print('id archivo', id_archivo)
                cargar_documento(id_archivo,name_document,request.user.id,tipo_de_plantilla)

                messages.success(request, "Documento firmado exitosamente.")
                return redirect('home')
            else:
                messages.error(request, "Debe buscar y seleccionar un documento primero.")

        elif action == 'reject':
            id_archivo = request.session.get('id_archivo')
            if id_archivo:
                print('id archivo', id_archivo)
                # Lógica para rechazar el documento
                #Actualizar el estado del documento (descomentar si necesario)
                rechazar_documento = Documento.objects.get(id=id_archivo)
                rechazar_documento.estado = 'RECHAZADO'
                rechazar_documento.fecha_finalizacion = timezone.now()
                rechazar_documento.save()
                messages.error(request, "El documento ha sido rechazado.")
                return redirect('home')
            else:
                messages.error(request, "Debe buscar y seleccionar un documento primero.")

        else:
            messages.error(request, "Acción no reconocida o falta documento.")

    context = {
        'documentos': nombre_documento,
        'doc_info': info,
        'doc_pdf': file_path
    }

    return render(request, template, context)


#Determinar lso documentod pendientes que tienes por liberar
def doc_pendientes():
    # Asegurándonos de que los Documentos están en el estado 'APROBADO'
   # Consulta ORM con condiciones
    documentos = Documento.objects.filter(
        estado='PREAPROBADO'
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

#metodo para obtener la datos de con respecto al nombre de documento
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
        estado='PREAPROBADO'
    ).values(
        'id', 'nombre_documento', 'id_linea__area__area', 'id_plantilla__nombre', 'revision_documento', 'autorizador'
    )
    
    return documentos


#Aqui tambien se obtiene los datos con respcto al ido dle documento con query
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
    
    

#Metodo para la cambiar la extension 
def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre




