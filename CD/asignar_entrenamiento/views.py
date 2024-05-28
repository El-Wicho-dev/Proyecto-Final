from django.shortcuts import render,redirect
from django.core.mail import send_mail
from Entrenamiento.models import Firma,EntrenamientoPuestoNomenclatura,Entrenamiento
from Documentos.models import Plantilla,Documento,Historial
from Usuarios.models  import Linea,Area,UsuarioPuesto,Puesto,PerfilUsuario
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse
from django.db.models import F, Value , CharField,Func,Q
from django.db.models.functions import Concat,Cast
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


# Create your views here.

#metodo para asignar los entrenamientos ccorrespoendies de los usuarios
def asignar_entrenamiento(request):
    template_name = 'Entrenamiento/asignar_entrenamiento.html'
    
    id_responsable = request.user.id
    print(id_responsable)
    doc_pendientes = pendientes(id_responsable)
    usuarios_activos = PerfilUsuario.objects.filter(estado='ACTIVO')
    puestos = Puesto.objects.order_by('descripcion_general').values_list('descripcion_general', flat=True).distinct()
    
    id_documento = None
    
    for documento in doc_pendientes:
        id_documento = documento.id_documento
        
    if not doc_pendientes:
        print("No ahi documentos pendientes por firmar")
        #messages.warning(request, 'No hay documentos pendientes para asignar.')
        

    if request.method == 'POST':
        usuarios_nombres = request.POST.getlist('usuarios[]')
        usuariobool = request.POST.get('usuariobool', 'default_value')


        print("POST data:", request.POST)
        print(usuarios_nombres)
        

        print("Usuarios nombres:", usuarios_nombres)
        
        nombres_puesto = []
        usuarios_ids = []
        descripciones_general = []
        lista_puestos_nomenclaturas = []
        
        
        if usuariobool == 'false':
            # Si la lista de nombres de usuarios está vacía, añade un mensaje de error
            messages.error(request, 'Por favor, seleccione al menos un usuario para el entrenamiento.')
            return  redirect("asignar_entrenamiento")
            # Puedes optar por redirigir al usuario de vuelta al formulario o simplemente cargar la página con el mensaje
        else:
            for nombre_completo in usuarios_nombres:
                print("Procesando nombre:", nombre_completo)        
                
                usuarios_puestos = UsuarioPuesto.objects.annotate(
                nombre_completo=Concat('usuario__first_name', Value(' '), 'usuario__last_name', output_field=CharField())
                ).filter(
                    nombre_completo=nombre_completo,
                    usuario__perfilusuario__estado='ACTIVO'
                )
                for up in usuarios_puestos:
                    print('xd' ,up.nombre_completo)


                for usuario_puesto in usuarios_puestos:
                    if usuario_puesto.usuario.id not in usuarios_ids:
                        usuarios_ids.append(usuario_puesto.usuario.id)
                        nombre_completo = f"{usuario_puesto.usuario.first_name} {usuario_puesto.usuario.last_name}"
                        nombres_puesto.append(nombre_completo)
                        descripcion_general = usuario_puesto.puesto.descripcion_general
                        descripciones_general.append(descripcion_general)
                        
                        lista_puestos_nomenclaturas.append((usuario_puesto.puesto.id))
                        print("Usuario activo agregado:", nombre_completo, "ID:", usuario_puesto.usuario.id, "Descripcion: " , usuario_puesto.puesto.descripcion_general, "id_puesto", usuario_puesto.puesto.id)
        

        
            print(usuarios_ids)
        
            # Lógica adicional para manejar los datos recibidos
            
            nomenclatura = calcular_nomenclatura(id_documento)
            print(nomenclatura)
            
            
            for puesto_id in lista_puestos_nomenclaturas:
                puesto = Puesto.objects.get(id=puesto_id)
                nuevo_entrenamiento = EntrenamientoPuestoNomenclatura(
                    id_puesto=puesto,
                    estado='ACTIVO',
                    fecha_registro=timezone.now(),
                    nomenclatura=nomenclatura,
                    id_unidad_negocio=None  # Siempre None como mencionaste
                )
                nuevo_entrenamiento.save()
                print(f"Guardado: {nuevo_entrenamiento}")
            
                
            for usuario_id in usuarios_ids:
                usuario = User.objects.get(id=usuario_id)
                doc = Documento.objects.get(id=id_documento)
                usuario_entrenamiento = Entrenamiento(
                    id_documento = doc,
                    id_usuario = usuario,
                    calificacion  = None,
                    estado = 'REALIZAR ENTRENAMIENTO'
                )
                usuario_entrenamiento.save()
                print(f"Guardado: {usuario_entrenamiento}")
                
                  
            asignar_entrenamientofun(id_responsable,id_documento)
            

    context = {
        'documentos': doc_pendientes,
        'puestos': puestos,
        'usuarios_activos': usuarios_activos
    }
    
    return render(request, template_name, context)



#metodo para cambiar el estauts al document una vez firmado el docuemnto de assingar a entrenamiento
def asignar_entrenamientofun(id_usuario,Id_Documento):
    # Actualizar el estado del documento
    Documento.objects.filter(
        id=Id_Documento, 
        estado='ASIGNAR ENTRENAMIENTO'
    ).update(
        estado='ENTRENAMIENTO'
    )

    documento = Documento.objects.get(id = Id_Documento)
    usuario = User.objects.get(id = id_usuario)
    # Insertar un nuevo registro en el historial de aprobación de entrenamientos
    nuevo_historial = Historial(
        id_documento=documento,
        id_responsable=usuario,  # Asumiendo que el ID del usuario está disponible a través de request.user
        fecha=timezone.now(),
        accion='ENTRENAMIENTO ASIGNADO'
    )
    nuevo_historial.save()



#query de base de datos apara calcular nommenclaturas
def calcular_nomenclatura(id_documento):
    # Función para calcular la nomenclatura del documento
    # Utilizamos annotations para concatenar diferentes campos de FK y construir la nomenclatura
    documento = Documento.objects.filter(id=id_documento).annotate(
        nomenclatura=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'), output_field=CharField())),
                default=F('consecutivo'),
                output_field=CharField()
            ),
            output_field=CharField()
        )
    ).first()
    
    return documento.nomenclatura if documento else None


#ajax de javascritp que manda los usuarios con respceto al puestos
def puestoajax (request):
    if request.method == 'POST':
        #print(request.POST)
        descripcion_puesto = request.POST.get('puesto')
        
        #print(descripcion_puesto)
        
        nombres_puesto = []
        
        # Suponiendo que 'PerfilUsuario' tiene un campo 'estado' y está relacionado con 'User'
        usuarios_puestos = UsuarioPuesto.objects.filter(
            puesto__descripcion_general=descripcion_puesto,
            usuario__perfilusuario__estado='ACTIVO'
        )
        usuarios_distinct = usuarios_puestos.values('usuario__first_name', 'usuario__last_name').distinct()


        for usuario in usuarios_distinct:
            nombre_completo = f"{usuario['usuario__first_name']} {usuario['usuario__last_name']}"
            nombres_puesto.append(nombre_completo)

        #print(nombres_puesto)
        
        return JsonResponse({'nombres_puesto': nombres_puesto})


    
    return JsonResponse({'error': 'Método no permitido'})




def obtener_datos_usuarios(usuarios_nombres):
    nombres_puesto = []
    usuarios_ids = []
    descripciones_general = []

    for nombre_completo in usuarios_nombres:
        print("Procesando nombre:", nombre_completo)        
        
        usuarios_puestos = UsuarioPuesto.objects.annotate(
        nombre_completo=Concat('usuario__first_name', Value(' '), 'usuario__last_name', output_field=CharField())
        ).filter(
            nombre_completo=nombre_completo,
            usuario__perfilusuario__estado='ACTIVO'
        )
        print("Usuarios puestos activos encontrados:", usuarios_puestos)

        for usuario_puesto in usuarios_puestos:
            if usuario_puesto.usuario.id not in usuarios_ids:
                usuarios_ids.append(usuario_puesto.usuario.id)
                nombre_completo = f"{usuario_puesto.usuario.first_name} {usuario_puesto.usuario.last_name}"
                nombres_puesto.append(nombre_completo)
                descripcion_general = usuario_puesto.puesto.descripcion_general
                descripciones_general.append(descripcion_general)
                
                print("Usuario activo agregado:", nombre_completo, "ID:", usuario_puesto.usuario.id, "Descripcion: " , usuario_puesto.puesto.descripcion_general)
   

    return nombres_puesto, usuarios_ids, descripciones_general




    


#QUERY PARA OBTENER LOS DOCUENTOS PENDIENTES PARA ASIGNAR ENTRENAMIENTO
def pendientes(id_usuario):
    documentos = Documento.objects.filter(id_responsable=id_usuario, estado='ASIGNAR ENTRENAMIENTO').order_by('nombre').annotate(
        consecutivo_formatted=Case(
            When(consecutivo='00', then=Value('00')),
            When(consecutivo__lt=10, then=Concat(Value('0'), 'consecutivo')),
            default=F('consecutivo'),
            output_field=CharField()
        )
    ).annotate(
        nombrexd=ExpressionWrapper(
            Concat(
                F('id_plantilla__codigo'),
                Value('-'),
                F('id_linea__codigo_linea'),
                Value(' '),
                F('consecutivo_formatted'),
                Value(' REV. '),
                F('revision_documento'),
                Value(' '),
                F('nombre')
            ),
            output_field=CharField()
        ),
        nombre_plantilla=F('id_plantilla__nombre'),  # Agregar el nombre de la plantilla
        area=F('id_linea__nombre_linea'),  # Agregar el nombre de la línea
        revision_actual = F('revision_documento'),
        id_documento=F('id')  # Agregar el ID del documento
    )
    
    for documento in documentos:
        print("nombrexd:", documento.nombrexd)
        print("nombre_plantilla:", documento.nombre_plantilla)
        print("area:", documento.area)
        print("Revision Actual:", documento.revision_actual)
        print("id_documento:", documento.id_documento)
    
    return documentos
