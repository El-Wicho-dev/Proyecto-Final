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



def convert_to_pdf(doc_path, output_path, watermark_text):
    # Construye la ruta completa al documento y al directorio de salida
    input_file = os.path.join(settings.MEDIA_ROOT, doc_path)
    output_dir = os.path.join(settings.MEDIA_ROOT, output_path)

    # Asegúrate de que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo de salida (sin la extensión)
    output_pdf_name = os.path.splitext(os.path.basename(doc_path))[0] + '.pdf'
    output_pdf_path = os.path.join(output_dir, output_pdf_name)
    
    # Ejecuta LibreOffice en modo headless para convertir el archivo
    subprocess.run([
        'libreoffice', '--headless', '--convert-to', 'pdf', '--outdir',
        output_dir, input_file
    ], check=True)

    # Ruta del archivo de marca de agua temporal
    watermark_file = os.path.join("watermark.pdf")

    # Genera el PDF de la marca de agua con texto centrado en diagonal

    # Genera el PDF de la marca de agua con texto centrado en diagonal
    subprocess.run([
        'gs', '-o', watermark_file, '-sDEVICE=pdfwrite',
        '-c', "/Helvetica-Bold findfont 120 scalefont setfont",  # Incrementa el tamaño de la fuente
        '-c', "1 0.82 0.86 setrgbcolor",  # Establece el color del texto
        '-c', "297.5 421 translate",  # Centra el origen en la mitad de una página A4
        '-c', "45 rotate",  # Rota el texto 45 grados
        '-c', "-350 -50 moveto",  # Ajusta para centrar el texto rotado
        '-c', f"({watermark_text}) show"
    ], check=True)



    # Construye el archivo PDF final con la marca de agua
    watermarked_pdf_path = os.path.join(output_dir, f"OBSOLETO_{output_pdf_name}")
    subprocess.run([
        'pdftk', output_pdf_path, 'background', watermark_file, 'output', watermarked_pdf_path
    ], check=True)

    os.remove(output_pdf_path)

def liberar(request):
    template = 'documentos/solicitar_liberacion.html'
    
    nombre_documento = doc_pendientes()
    
    
    action = request.POST.get('action')
    comment = request.POST.get('comment', '')
    print(request.POST)
    


    documento_seleccionado = request.session.get('documentos', [])

    if not documento_seleccionado:
        request.session.pop('documentos', None)
        documento_seleccionado = []  # Asegura que la lista esté vacía

    info = None
    file_path = None

    if documento_seleccionado:
        id_archivo = documento_seleccionado[0]['id']
        print("id documento:", id_archivo)
        
        name_document = documento_seleccionado[0]['nombre_documento']
        print("El nombre obtenido con ajax", name_document)        
        
        info = informaciondocs(id_archivo)
        
        if info:
            linea_documento = info.Linea
            tipo_de_plantilla = info.Plantilla_Nombre
            documento_pdf = cambiar_la_extencion(name_document)
            print("nueva extensión", documento_pdf)
        
            if documento_pdf:
                file_path = os.path.join(settings.MEDIA_URL, 'Control_de_documentos_pdfs', tipo_de_plantilla, linea_documento, documento_pdf)
                print("ruta : ", file_path)
            else:
                file_path = None  # No hay documento disponible
                
    
        if action == 'sign':
                print("entre al boton de firmar")
                if not nombre_documento:
                    messages.error(request, "No hay documentos seleccionados.")
                    return render(request, template, {
                        'documentos': nombre_documento,
                        'entrenamiento_info': [],
                        'doc_pdf': None
                    })
                        
                cargar_documento(id_archivo, name_document, request.user.id)
                messages.success(request, "Documento firmado exitosamente.")
                return redirect('home')

        elif action == 'reject':
                print("entre al boton de rechazar")
                
                if not nombre_documento:
                    messages.error(request, "No hay documentos seleccionados.")
                    return render(request, template, {
                        'documentos': nombre_documento,
                        'entrenamiento_info': [],
                        'doc_pdf': None
                    })
                """"
                # Actualizar el estado del documento
                rechazar_documento = Documento.objects.get(id=id_documento)
                rechazar_documento.estado = 'RECHAZADO'
                rechazar_documento.fecha_finalizacion = timezone.now()
                rechazar_documento.save()
                """
                
                
                
                messages.error(request, "El documento ha sido rechazado.")
                return redirect('home')

    context = {
        'documentos': nombre_documento,
        'doc_info': info,
        'doc_pdf': file_path
    }
    
    return render(request, template, context)



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

def informaciondocs(id_documento):
    documento = (
        Documento.objects
        .filter(id=id_documento)
        .annotate(
            Responsable=Concat(F('id_responsable__first_name'), Value(' '), F('id_responsable__last_name'), output_field=CharField()),
            Reviso=Concat(F('revisador__first_name'), Value(' '), F('revisador__last_name'), output_field=CharField()),
            Autorizo=Concat(F('aprobador__first_name'), Value(' '), F('aprobador__last_name'), output_field=CharField()),
            Nombre_Documento=Concat(
                F('id_plantilla__codigo'),
                Value('-'),
                F('id_linea__codigo_linea'),
                Value(' '),
                Cast(F('consecutivo'), CharField()),
                Value(' REV.'),
                F('revision_documento'),
                Value(' '),
                F('nombre'),
                output_field=CharField()
            ),
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
    if documento:
        print("Responsable:", documento.Responsable)
        print("Reviso:", documento.Reviso)
        print("Autorizo:", documento.Autorizo)
        print("Nombre Documento:", documento.Nombre_Documento)
        print("Rev Documento:", documento.Rev_Documento)
        print("Rev Plantilla:", documento.Rev_Plantilla)
        print("Nombre Plantilla:", documento.Plantilla_Nombre)
        print("Area:", documento.Area)
        print("Linea:", documento.Linea)
        print("ID Firma Reviso:", documento.Id_Firma_Reviso)
        print("ID Firma Autorizo:", documento.Id_Firma_Autorizo)
        print("Tipo de Area:", documento.id_plantilla.tipo_de_area)

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

def cambiar_la_extencion(nombre_documento):
    # Separar el nombre base y la extensión
    base_nombre, ext = os.path.splitext(nombre_documento)
    
    # Cambiar la extensión a .pdf
    if ext in ['.docx', '.doc']:
        nuevo_nombre = f"{base_nombre}.pdf"
    
    return nuevo_nombre




