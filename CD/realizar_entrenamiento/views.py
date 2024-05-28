from django.shortcuts import render,redirect
from Documentos.models import Documento,Plantilla,Historial
from Usuarios.models import Linea
from Entrenamiento.models import Entrenamiento
from django.db.models.functions import Concat
from django.db.models import Value,Case,When,F,CharField
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from home.views import home

# Create your views here.
#Se renderiza el formulario para realizar el matriz de entrenamiento
def encuesta(request):
    template_name = "Entrenamiento/realizar_entrenamiento.html"
    
    
    id_usuario = request.user.id
        
    nombre_documento = documentos(id_usuario)
    
    rev_documentos = Documento.objects.order_by('revision_documento').values_list('revision_documento', flat=True).distinct()
    plantillas = Plantilla.objects.order_by('nombre').values_list('nombre', flat=True)
    areas = Linea.objects.order_by('area__area').values_list('area__area', flat=True).distinct()

        # Suponiendo que tu modelo User utiliza first_name y last_name
    aprobadores = Documento.objects.filter(
    aprobador__isnull=False
    ).annotate(
        nombre_completo=Concat('aprobador__first_name', Value(' '), 'aprobador__last_name')
    ).order_by('nombre_completo').values_list('nombre_completo', flat=True).distinct()
    
    if request.method == 'POST':
        
        
        # Capturar el valor enviado desde el formulario
        nombre_documento = request.POST.get('nombre_documento')
        linea_area = request.POST.get('area_seleccionada')
        tipo_documento = request.POST.get('plantilla_seleccionada')
        numero_revision = request.POST.get('revision_documento')
        descripcion = request.POST.get('en_que_consiste')
        autorizacion = request.POST.get('autor')
        
        if not nombre_documento:
            messages.error(request,"No existe nigun documento todavia para realizar entrenamiento")
            return redirect('encuesta')

        print('nombre_documento:', nombre_documento, 'linea_seleccionado:', linea_area, 'tipo_documento:', tipo_documento, 'numero_revision:', numero_revision, 'descripcion:', descripcion, 'autorizacion:', autorizacion) 

        
        documento_seleccionado = select_documento(nombre_documento)
        
        id_archivo = None
        
        for documento in documento_seleccionado:
            id_archivo = documento['id']
            nombre_archivo = documento['nombre_documento']
            linea = documento['id_linea__area__area']
            nombre = documento['id_plantilla__nombre']
            rev = documento['revision_documento']
            autorizador = documento['autorizador']

            # Ahora puedes usar estas variables como necesites
            print(f"ID Archivo: {id_archivo}, Nombre Archivo: {nombre_archivo}, Línea: {linea}, Nombre: {nombre}, Revisión: {rev}, Autorizador: {autorizador}")
        
        buenas = 0

        for documento in documento_seleccionado:
            if documento['id_linea__area__area'] == linea_area:
                buenas += 1
            if documento['nombre_documento'] == tipo_documento:
                buenas += 1
            if documento['revision_documento'] == numero_revision:
                buenas += 1
            if documento['autorizador'] == autorizacion:
                buenas += 1

        if len(descripcion) >= 10:
            print("si es buena descripcion")
            buenas += 1
        
        
           # Mostrar calificación
        mensaje = "Su calificación es: " + str(buenas) + "/5"
        if buenas < 4:
            mensaje += ". Le recomendamos volver a tomar el entrenamiento, ya que con esta calificación no se podrá liberar su entrenamiento."
            messages.error(request, mensaje)
        else:
            mensaje += "Entrenamiento Realizado correctamente"
            messages.success(request, mensaje)
            Entrenamiento.objects.filter(id_documento=id_archivo,id_usuario=id_usuario).update(calificacion=buenas,fecha=timezone.now())


        bandera = verificar_firma_documentos(id_archivo)
        print('TU BANDERA ES: ',bandera)
        
        if bandera:
            Documento.objects.filter(id=id_archivo).update(estado='APROBAR ENTRENAMIENTO')
            
            documento = Documento.objects.get(id=id_archivo)
            usuario = User.objects.get(id=id_usuario)
            
            alta_historial = Historial.objects.create(
                id_documento=documento,
                id_responsable=usuario,
                fecha=timezone.now(),
                accion='ENTRENAMIENTO FINALIZADO AL 100%'
            )
            alta_historial.save()
    
        
        return redirect('encuesta')
    context = {
        'documentos':nombre_documento,
        'areas':areas,
        'plantillas':plantillas,
        'rev_documentos':rev_documentos,
        'aprobadores':aprobadores,
        
    }
    return render(request,template_name,context)


#Query de base de datos para consultar los documentos que estan en entrenamient con respecto al usuario 
def documentos(id_usuario):
     # Consulta con ORM de Django
    entrenamientos = Entrenamiento.objects.filter(
        id_usuario__id=id_usuario,  
        calificacion__isnull=True,
        id_documento__estado='ENTRENAMIENTO'
    ).select_related('id_documento', 'id_documento__id_plantilla', 'id_documento__id_linea').annotate(
        Nombre_Documento=Concat(
            'id_documento__id_plantilla__codigo', Value('-'),
            'id_documento__id_linea__codigo_linea', Value(' '),
            Case(
                When(id_documento__consecutivo='00', then=Value('00')),
                When(id_documento__consecutivo__lt=10, then=Concat(Value('0'), F('id_documento__consecutivo'))),
                default=F('id_documento__consecutivo'),
                output_field=CharField(),
            ),
            Value(' REV. '),
            'id_documento__revision_documento',
            Value(' '),
            'id_documento__nombre',
            output_field=CharField()
        )
    )

    # Podrías iterar sobre los resultados como este ejemplo:
    for entrenamiento in entrenamientos:
        print(entrenamiento.Nombre_Documento)
        
    return entrenamientos

#Query esete query sirve para determnar infromacion con respecto al documento seleccionado
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
        estado='ENTRENAMIENTO'
    ).values(
        'id', 'nombre_documento', 'id_linea__area__area', 'id_plantilla__nombre', 'revision_documento', 'autorizador'
    )
    
    return documentos

    
#Este metodo verifica si el document oesta en relizar entrenamiento y si el suario esta activo
def verificar_firma_documentos(id_documento):
    usuarios_que_no_han_firmado = Entrenamiento.objects.filter(
        id_documento=id_documento, 
        calificacion__isnull=True,  # Verifica si la calificación es nula
        id_usuario__perfilusuario__estado='ACTIVO',
        estado = 'REALIZAR ENTRENAMIENTO'# Filtra por usuarios activos
    ).exists()
    return not usuarios_que_no_han_firmado
