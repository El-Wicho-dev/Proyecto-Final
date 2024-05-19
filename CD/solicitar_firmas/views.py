from django.shortcuts import render,redirect
from Documentos.forms import DocumentoForm, FormatosPermitidosForm
from Documentos.models import FormatosPermitidos,Documento,Plantilla,Historial,DocumentoBloqueado
from Usuarios.models import Linea
from Entrenamiento.models import Firma
from Entrenamiento.models import Entrenamiento
from Usuarios.models import Puesto,UsuarioPuesto
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat, Cast
from django.db.models.expressions import Case, When
import os
from django.utils import timezone
from func.correos import send_correo_ordinario  # Asumiendo que tu función está en utils.py
from django.http import HttpResponse,JsonResponse


def ajax_filtrar_usuarios(request):
    # Obtener el autor una vez
    autor_id = request.user.id
    autor_nombre = f"{request.user.first_name} {request.user.last_name}".strip()
    
    selected_revisador = request.GET.get('selected_revisador')
    selected_aprobador = request.GET.get('selected_aprobador')
    
    id_plantilla = request.GET.get('tipo_de_archivo')
    plantillas = Plantilla.objects.get(id = id_plantilla)
    tipo_de_archivo = plantillas.nombre
    revisador = plantillas.revisador
    aprobador = plantillas.aprobador
    print(request.GET)
    

    
     # Encuentra los puestos que coincidan con los roles de revisador y aprobador
    puestos_revisadores = Puesto.objects.filter(descripcion_general=revisador)
    puestos_aprobadores = Puesto.objects.filter(descripcion_general=aprobador)
    puestos_aprobadores_gerentes = Puesto.objects.filter(descripcion_general__icontains='GERENTE')

    print(puestos_aprobadores_gerentes)

    # Encuentra los usuarios para cada rol y los serializa
    usuarios_liberadores = [
        {"id": user.id, "nombre_completo": f"{user.first_name} {user.last_name}"} 
        for user in User.objects.filter(usuariopuesto__puesto__in=puestos_revisadores).distinct()
    ]
    
    if aprobador == 'Gerente de Departamento':
          usuarios_aprobadores = [
            {"id": user.id, "nombre_completo": f"{user.first_name} {user.last_name}"} 
            for user in User.objects.filter(usuariopuesto__puesto__in=puestos_aprobadores_gerentes).distinct()
        ]
    else:
        usuarios_aprobadores = [
        {"id": user.id, "nombre_completo": f"{user.first_name} {user.last_name}"} 
        for user in User.objects.filter(usuariopuesto__puesto__in=puestos_aprobadores).distinct()
        ]
    
    print(usuarios_aprobadores)
    print(usuarios_aprobadores)
        

    return JsonResponse({'liberadores': usuarios_liberadores, 'aprobadores': usuarios_aprobadores,'autor_id': autor_id, 'autor':autor_nombre})


# Create your views here.

def solicitar(request):
    template_name = 'documentos/solicitar_firmas.html'
    # Suponiendo que FormatosPermitidosForm es tu forma de manejar las extensiones permitidas
    extensiones_permitidas = [ext[0] for ext in FormatosPermitidos.extension_documentos_choices]

    if request.method == 'POST':
        documento_form = DocumentoForm(request.POST, request.FILES)
        
        print(request.POST)
        id_plantilla = request.POST.get('id_plantilla')
        id_revisador = request.POST.get('revisador')
        id_aprobador = request.POST.get('aprobador')
        comentarios = request.POST.get('comentarios')

        print("ID de la plantilla:", id_plantilla)
        print("ID del responsable:", request.user.id)
        print("ID del revisador:", id_revisador)
        print("ID del aprobador:", id_aprobador)
        print("comentarios:", comentarios)
        

        responsable = User.objects.get(id=request.user.id)
        revisador = User.objects.get(id=id_revisador)
        aprobador = User.objects.get(id=id_aprobador)

        nombre_completo_responsable = f"{responsable.first_name} {responsable.last_name}"
        nombre_completo_liberador = f"{revisador.first_name} {revisador.last_name}"
        nombre_completo_aprobador = f"{aprobador.first_name} {aprobador.last_name}"

        print("Nombre completo del responsable:", nombre_completo_responsable)
        print("Nombre completo del revisador:", nombre_completo_liberador)
        print("Nombre completo del aprobador:", nombre_completo_aprobador)

        nom_archivo = request.FILES['editable_document'].name

        # Dividimos el nombre del archivo en partes
        nombre_documento = nom_archivo.split(' ')
        id_documento = nombre_documento[0].split('-')[0]  # 'FS'
        id_linea = nombre_documento[0].split('-')[1]      # 'L2'
        consecutivo = nombre_documento[1]                  # '00'

        # La revisión puede estar en la tercera parte, necesitamos dividir por el punto para obtener '01'
        # Asumimos que 'REV.' siempre precede a la revisión
        rev_index = nombre_documento.index('REV.') + 1     # Encontrar el índice de 'REV.' y sumar 1 para obtener el índice de la revisión
        rev = nombre_documento[rev_index].split('.')[0]    # Extraer '01'

        # Combinar todas las partes del nombre del documento, desde después de la revisión hasta el final, excluyendo la extensión
        nombre_del_documento = ' '.join(nombre_documento[rev_index + 1:]).rsplit('.', 1)[0]

        # Extraer la extensión del nombre del archivo original
        extension = nom_archivo.split('.')[-1]            # 'docx'

        nombre_con_extencion = nombre_del_documento + '.' + extension
        
        plantillas = Plantilla.objects.get(codigo=id_documento)
        revicion_actual = plantillas.revision_actual
        
        lineas = Linea.objects.get(codigo_linea= id_linea)
        id_linea_num = lineas.id

        id_responsable = request.user.id
        responsable = User.objects.get(id=id_responsable)


        


        # Búsqueda de usuarios por nombre completo aproximado
        quien_libera = User.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__icontains=nombre_completo_liberador).first()
        quien_aprueba = User.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__icontains=nombre_completo_aprobador).first()

        print("Usuario que libera:", quien_libera)
        print("Usuario que aprueba:", quien_aprueba)


        
        print("Id_plantilla:", plantillas) #YA
        print("Linea:", id_linea) #YA
        print("Id_lineanum:", id_linea_num)
        print("id_user autor :", request.user.id)
        print("Nombre del archivo:", nombre_del_documento)
        print("ID del documento:", id_documento)
        print("id del liberador" , revisador)
        print("id del aprobador" , aprobador)
        print("Revisión de documento:", rev)
        print("Revisión de documento:", revicion_actual)
        print("Consecutivo:", consecutivo)
        print("Extensión del archivo:", extension)
        print("Comentarios del Documento:", comentarios)
        
     
        
        
        documento = Documento.objects.create(
        id_plantilla=plantillas,
        id_linea=lineas,
        id_responsable=responsable,
        nombre=nombre_con_extencion,
        revisador=revisador,
        aprobador=aprobador,
        estado='REVISION',
        fecha_finalizacion = None,
        revision_de_plantilla =revicion_actual,
        revision_documento=rev,
        consecutivo=consecutivo,
        extension=extension,
        comentarios=comentarios
        )
        
         #Asignar firmas
        
        Firma.objects.create(id_documento=documento, id_liberador=revisador,firma = None)
        Firma.objects.create(id_documento=documento, id_liberador=aprobador,firma = None)
        Firma.objects.create(id_documento=documento, id_liberador=responsable, firma=timezone.now())
    
        messages.success(request,"Se ha solicitado con exito la liberación")
    
        return redirect('solicitar')
        
    else:
        documento_form = DocumentoForm()

    context = {
        'documento_form': documento_form,
        'extensiones_permitidas': extensiones_permitidas,
    }
    
    return render (request,template_name,context)


def send_test_email(request):
    # Datos de prueba para el correo
    to_email = 'luis.jimenez201@tectijuana.edu.mx '
    subject = 'Correo Importante'
    factory_name = 'UMTRACK'
    title = '¡Bienvenido a UMTRACK!'
    message = 'Estamos encantados de tenerte a bordo.'
    link = 'http://127.0.0.1:8000/'

    # Llamada a la función de envío de correo
    send_correo_ordinario(to_email, subject, factory_name, title, message, link)
    return HttpResponse("Correo enviado exitosamente!")
