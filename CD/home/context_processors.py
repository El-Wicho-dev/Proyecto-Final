# home/context_porcessors.py.py

from django.db.models import Count, Q, Value, CharField
from django.contrib.auth.models import User
from django.urls import reverse
from Documentos.models import Documento
from Entrenamiento.models import Entrenamiento,Firma
from Usuarios.models import UsuarioPuesto
from django.db.models.functions import Concat
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#query para obtener las notificaciones correspondiente del cada usuario correspondientes 
#usando un context_porcessors
def notificaciones_context(request):
    if not request.user.is_authenticated:
        return {}
    
    user_id = request.user.id
    user_full_name = f"{request.user.first_name} {request.user.last_name}"
    
    puesto_descripcion_Documentos = 'Ingeniero de Sistemas de Gestión'
    puesto_descripcion_Entrenamiento = 'Coordinador de Entrenamiento'

    esperando_liberacion_count = 0
    preaprobados_count  = 0
    
    
    # Verificar si el usuario tiene el puesto específico
    tiene_puesto_Documentos = UsuarioPuesto.objects.filter(
        usuario_id=user_id,
        puesto__descripcion_general=puesto_descripcion_Documentos
    ).exists()
    
    
     # Verificar si el usuario tiene el puesto específico
    tiene_puesto_Entrenamiento = UsuarioPuesto.objects.filter(
        usuario_id=user_id,
        puesto__descripcion_general=puesto_descripcion_Entrenamiento
    ).exists()

    #liberar documento
    if tiene_puesto_Documentos:
        preaprobados_count = Documento.objects.filter(estado='PREAPROBADO').count()
        
    
    
    asignaciones_pendientes = Documento.objects.filter(
        id_responsable=user_id,
        estado='ASIGNAR ENTRENAMIENTO'
    ).annotate(
        nombre_completo=Concat(
            'id_plantilla__codigo', Value('-'),
            'id_linea__codigo_linea', Value(' '),
            'consecutivo', Value(' REV. '),
            'revision_documento', Value(' '), 'nombre',
            output_field=CharField()
        )
    ).order_by('nombre').count()


    if tiene_puesto_Entrenamiento:
        esperando_liberacion_count = Documento.objects.filter(estado='APROBAR ENTRENAMIENTO').count()
    
    documentos_por_firmar_count = Documento.objects.filter(
        estado='REVISION',
        firmas__firma__isnull=True,
        firmas__id_liberador=user_id,
    ).count()
    
    entrenamientos_pendientes = Entrenamiento.objects.filter(
        id_usuario=user_id,
        id_documento__estado='ENTRENAMIENTO',
        calificacion__isnull=True
    ).count()

    total_notificaciones = (preaprobados_count + asignaciones_pendientes +
                            esperando_liberacion_count + documentos_por_firmar_count +
                            entrenamientos_pendientes)

    contexto = {
        'preaprobados_count': preaprobados_count,
        'asignaciones_pendientes': asignaciones_pendientes,
        'esperando_liberacion_count': esperando_liberacion_count,
        'documentos_por_firmar_count': documentos_por_firmar_count,
        'entrenamientos_pendientes': entrenamientos_pendientes,
        'url_liberar_documento': reverse('liberar-documento'),
        'url_asignar_entrenamiento': reverse('asignar_entrenamiento'),
        'url_aprobar_entrenamiento': reverse('aprobar_entrenamiento'),
        'url_aprobar_documento': reverse('aprobar'),
        'url_encuesta_entrenamiento': reverse('encuesta'),
        'total_notificaciones': total_notificaciones
    }
    
    return contexto



def emit_notification_updates(request):
    if not request.user.is_authenticated:
        return {}
    
    user_id = request.user.id
    user_full_name = f"{request.user.first_name} {request.user.last_name}"
    
    puesto_descripcion_Documentos = 'Ingeniero de Sistemas de Gestión'
    puesto_descripcion_Entrenamiento = 'Coordinador de Entrenamiento'

    esperando_liberacion_count = 0
    preaprobados_count  = 0
    
    
    # Verificar si el usuario tiene el puesto específico
    tiene_puesto_Documentos = UsuarioPuesto.objects.filter(
        usuario_id=user_id,
        puesto__descripcion_general=puesto_descripcion_Documentos
    ).exists()
    
    
     # Verificar si el usuario tiene el puesto específico
    tiene_puesto_Entrenamiento = UsuarioPuesto.objects.filter(
        usuario_id=user_id,
        puesto__descripcion_general=puesto_descripcion_Entrenamiento
    ).exists()

    #liberar documento
    if tiene_puesto_Documentos:
        preaprobados_count = Documento.objects.filter(estado='PREAPROBADO').count()
        
    
    
    asignaciones_pendientes = Documento.objects.filter(
        id_responsable=user_id,
        estado='ASIGNAR ENTRENAMIENTO'
    ).annotate(
        nombre_completo=Concat(
            'id_plantilla__codigo', Value('-'),
            'id_linea__codigo_linea', Value(' '),
            'consecutivo', Value(' REV. '),
            'revision_documento', Value(' '), 'nombre',
            output_field=CharField()
        )
    ).order_by('nombre').count()


    if tiene_puesto_Entrenamiento:
        esperando_liberacion_count = Documento.objects.filter(estado='APROBAR ENTRENAMIENTO').count()
    
    documentos_por_firmar_count = Documento.objects.filter(
        estado='REVISION',
        firmas__firma__isnull=True,
        firmas__id_liberador=user_id,
    ).count()
    
    entrenamientos_pendientes = Entrenamiento.objects.filter(
        id_usuario=user_id,
        id_documento__estado='ENTRENAMIENTO',
        calificacion__isnull=True
    ).count()

    total_notificaciones = (preaprobados_count + asignaciones_pendientes +
                            esperando_liberacion_count + documentos_por_firmar_count +
                            entrenamientos_pendientes)

    notification_data  = {
        'preaprobados_count': preaprobados_count,
        'asignaciones_pendientes': asignaciones_pendientes,
        'esperando_liberacion_count': esperando_liberacion_count,
        'documentos_por_firmar_count': documentos_por_firmar_count,
        'entrenamientos_pendientes': entrenamientos_pendientes,
        'url_liberar_documento': reverse('liberar-documento'),
        'url_asignar_entrenamiento': reverse('asignar_entrenamiento'),
        'url_aprobar_entrenamiento': reverse('aprobar_entrenamiento'),
        'url_aprobar_documento': reverse('aprobar'),
        'url_encuesta_entrenamiento': reverse('encuesta'),
        'total_notificaciones': total_notificaciones
    }
    
    
    # Obtén el channel layer
    channel_layer = get_channel_layer()

    # Envía los datos al grupo
    async_to_sync(channel_layer.group_send)(
        "notifications_group",  # Asegúrate de que el grupo esté correctamente configurado en tu consumer
        {
            "type": "notification.message",  # El handler en tu consumer que manejará este mensaje
            "message": notification_data
        }
    )
