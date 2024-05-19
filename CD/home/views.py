from django.shortcuts import render
from Documentos.models import Documento
from Entrenamiento.models import Entrenamiento
from django.db.models import Value, CharField
from django.db.models.functions import Concat

# Create your views here.

def home(request):
    
    
    user_id = request.user.id
    user_full_name = f"{request.user.first_name} {request.user.last_name}"  # Así podrías obtener el nombre completo si no tienes un método específico

    
     # Contar documentos con estado 'PREAPROBADO'
    preaprobados_count = Documento.objects.filter(estado='PREAPROBADO').count()
    
    # Asignaciones de entrenamiento pendientes
    asignaciones_pendientes = Documento.objects.filter(
        id_responsable_id=user_id,
        estado='ASIGNAR ENTRENAMIENTO'
    ).annotate(
        nombre_completo=Concat(
            'id_plantilla__codigo', Value('-'),
            'id_linea__codigo', Value(' '),  # Asegúrate de que 'codigo' es el campo correcto en el modelo Linea
            'consecutivo', Value(' REV. '),
            'revision_documento', Value(' '), 'nombre',
            output_field=CharField()
        )
    ).order_by('nombre')
    
    # Documentos pendientes por liberación final
    esperando_liberacion_count = Documento.objects.filter(estado='ESPERANDO LIBERACION').count()
    
    # Documentos pendientes por firmar
    documentos_por_firmar_count = Documento.objects.filter(
        estado='REVISION',
        firmas__firma__isnull=True,
        firmas__id_liberador__first_name=request.user.first_name,  # Esto supone que el nombre está en 'first_name', ajustar según tu modelo
        firmas__id_liberador__last_name=request.user.last_name
    ).count()
    
    # Entrenamientos pendientes
    entrenamientos_pendientes = Entrenamiento.objects.filter(
        id_usuario_id=user_id,
        id_documento__estado='ENTRENAMIENTO',
        calificacion__isnull=True
    ).count()
    
    
    
    contexto ={
        'preaprobados_count': preaprobados_count,
        'asignaciones_pendientes': asignaciones_pendientes,
        'esperando_liberacion_count': esperando_liberacion_count,
        'documentos_por_firmar_count': documentos_por_firmar_count,
        'entrenamientos_pendientes': entrenamientos_pendientes
    }
    return render(request,"home/home.html",contexto)



