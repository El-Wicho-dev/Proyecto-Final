from django.shortcuts import render,redirect
from django.core.mail import send_mail
from Entrenamiento.models import Firma,EntrenamientoPuestoNomenclatura,Entrenamiento
from Documentos.models import Plantilla,Documento,Historial
from Usuarios.models  import Linea,Area,UsuarioPuesto,Puesto
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse
from django.db.models import F, Value , CharField,Func,Q
from django.db.models.functions import Concat,Cast
from django.db.models.expressions import Case, When
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from django.contrib import messages
from django.db import transaction
from urllib.parse import quote
from django.conf import settings
from func.clases_de_documento import nomenclatura
import re
from docx2pdf import convert
import os


# Create your views here.


def aprobar(request):
    template_name = 'documentos/aprobar_documento.html'
    id_interesado = request.user.id  # Autenticación de usuario        
    documentos_pendientes = Documento.CD_Firma_Documento_Pendiente(id_interesado)

    if request.method == 'POST':
        action = request.POST.get('action')
        comentario = request.POST.get('comment', '')

        nombre_documento = request.POST.get('reviewInput', '').strip()
        documento_buscar = Documento.CD_Firma_Documento_Pendiente(id_interesado).filter(nombre_documento__contains=nombre_documento)
        
        if not nombre_documento:
                messages.error(request, "No ha seleccionado ningún documento para firmar o rechazar.")
                return redirect('aprobar')  # Return to the form page with an error message
        
        print(comentario)
        if action == 'sign':
            

            id_documento = None
            codigo_plantilla = None
            
            

            for documento in documento_buscar:
                id_documento = documento.id
                
                Historial.objects.create(
                id_documento=documento,
                id_responsable=request.user,
                fecha=timezone.now(),
                accion='FIRMADO'
                )
                
                
                Firma.objects.filter(id_documento=documento, id_liberador=request.user).update(firma=timezone.now())
                codigo_plantilla = documento.codigo_plantilla
                firmas_pendientes = Firma.objects.filter(id_documento=documento, firma__isnull=True)

                messages.success(request, 'El documento ha sido firmado.')

            print(id_documento)

            if not firmas_pendientes.exists():
                Documento.objects.filter(id=id_documento).update(estado = 'ASIGNAR ENTRENAMIENTO')
                messages.success(request, 'El documento ha sido liberado. No hay firmas pendientes.')
                return redirect('home')  # Redirige para evitar reenvíos de formularios  
            
            
            
            return redirect('aprobar')  # Redirige para evitar reenvíos de formularios  
        elif action == 'reject':
            id_documento = None
            codigo_plantilla = None
            for documento in documento_buscar:
                id_documento = documento.id
                
                messages.error(request, 'El documento ha sido rechazado.')
                print('recibi el id: ', id_documento)
                Documento.objects.filter(id=id_documento).update(estado = 'RECHAZADO',fecha_finalizacion= timezone.now())
            return redirect('aprobar')   # Redirige para evitar reenvíos del formulario

            
    else:
        context = {
            'documentos': documentos_pendientes,
        }
        return render(request, template_name, context)




def get_document_url(request):
    if request.method == 'POST' and request.body:
        data = json.loads(request.body)
        nombre_documento = data.get('id_documento', '')
        nombre_documento = nombre_documento.replace('.docx', '.pdf')
    
        print(nombre_documento)
        
        no_documento,no_linea,consecutivo,revision,nombre_del_documento = nomenclatura(nombre_documento)
        
        plantillas = Plantilla.objects.get(codigo=no_documento)
        nombre_plantilla = plantillas.nombre
        
        lineas = Linea.objects.get(codigo_linea= no_linea)
        nombre_linea = lineas.nombre_linea
        
        # Asegúrate de que los nombres de archivos estén correctamente URL-encoded
        # si tienen espacios o caracteres especiales
       
        nombre_documento = quote(nombre_documento)
        
    
        # Construir la URL del documento PDF    
        url = f"{settings.RUTA_PDF_DOCUMENTOS}{nombre_plantilla}/{nombre_linea}/{nombre_documento}"
        
        if settings.DEBUG:
            url = f"http://127.0.0.1:8000{url}"
        
        return JsonResponse({'url': url}, status=200)
    else:
        return JsonResponse({'error': 'No se recibieron datos o la solicitud no es POST'}, status=400)






def calcular_nomenclatura(id_documento):
    # Función para calcular la nomenclatura del documento
    # Utilizamos annotations para concatenar diferentes campos de FK y construir la nomenclatura
    documento = Documento.objects.filter(id=id_documento).annotate(
        nomenclatura=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value('Rev. '),
            F('consecutivo'), Value(' '),
            F('revision_documento'), Value(' '),
            output_field=CharField()
        )
    ).first()
    
    return documento.nomenclatura if documento else None


def queryorm(id_interesado):
    documentos = Documento.objects.filter(
        estado__in=['APROBADO', 'REVISION'],
        firmas__firma__isnull=True,
        firmas__id_liberador=id_interesado
    ).annotate(
        nombre_documento=Concat(
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
        ),
        codigo_linea=F('id_linea__codigo_linea'),
        codigo_plantilla=F('id_plantilla__codigo'),
        consecutivo_format=Case(
            When(consecutivo='00', then=Value('00')),
            When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'))),
            default=F('consecutivo'),
            output_field=CharField()
        )
    ).select_related('id_linea', 'id_plantilla').prefetch_related('firmas')

    for doc in documentos:
        print(f"Nombre del Documento:{doc.nombre_documento}")
        print(f"Código de Línea: {doc.codigo_linea}")
        print(f"Código de Plantilla: {doc.codigo_plantilla}")
        print(f"Consecutivo Formateado: {doc.consecutivo_format}")
        print(f"Revisión del Documento: {doc.revision_documento}")
        print(f"Estado del Documento: {doc.estado}")

        print("----------------------------------------")

    return documentos


def obtener_correos_para_entrenamiento(nomenclatura):
    # Consultar puestos activos con la nomenclatura dada
    entrenamientos_puestos = EntrenamientoPuestoNomenclatura.objects.filter(
        nomenclatura=nomenclatura,
        estado='ACTIVO'
    ).select_related('id_puesto')  # Suponiendo que `puesto` es una relación ForeignKey en EntrenamientoPuestoNomenclatura

    # Listas para mantener los correos y IDs de usuarios
    correos = []
    id_usuarios = []

    # Iterar sobre los resultados para obtener los correos e IDs de usuario asociados a los puestos
    for ep in entrenamientos_puestos:
        usuarios_puestos = UsuarioPuesto.objects.filter(
            puesto=ep.id_puesto  # Corrección: se debe referenciar a ep.puesto en lugar de ep.id_puesto si `puesto` es la ForeignKey
        ).select_related('usuario')  # Optimización: traer información del usuario en la misma consulta

          # Gather emails of users ensuring no duplicates, and collecting user IDs
        for usuario_puesto in usuarios_puestos:
            usuario = usuario_puesto.usuario
            if usuario.email and usuario.email not in correos:
                correos.append(usuario.email)
            if usuario.id not in id_usuarios:
                id_usuarios.append(usuario.id) # Corrección: cambiar [] por () para append

    return correos, id_usuarios  # Retorna ambas listas
