from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Importa esto para manejar correctamente la zona horaria
from Usuarios.models import Linea
from datetime import date
from django.db.models.functions import Concat,Cast
from django.db.models import F, Value , CharField,Func
from django.db.models.expressions import Case, When


# Create your models here.


# Modelo para Liberaciones
class Liberacion(models.Model):
    liberacion = models.IntegerField()
    descripcion = models.TextField()

    def __str__(self):
        return f"Liberacion {self.liberacion}"


# Modelo para Plantillas
class Plantilla(models.Model):
    
    nombres_plantillas_choices = [
        ('FORMATOS','FORMATOS'),
        ('GUIAS','GUIAS'),
        ('AYUDA VISUAL','AYUDA VISUAL'),
        ('DIAGRAMA DE FLUJO', 'DIAGRAMA DE FLUJO'),
    ]
    nombres_autor_choices = [
        ('Dueño del proceso o su designado','Dueño del proceso o su designado'),
        ('Ingeniero de Manufactura','Ingeniero de Manufactura'),
        ('Ingeniero de Sistemas de Gestión','Ingeniero de Sistemas de Gestión'),
    ]
    nombres_aprobado_choices = [
    ('Gerente de Calidad', 'Gerente de Calidad'),
    ('Gerente de Departamento', 'Gerente de Departamento'),
    ('Gerente de Planta', 'Gerente de Planta'),
    ('Ingeniero de Calidad', 'Ingeniero de Calidad'),
    ('Supervisor de Producción', 'Supervisor de Producción'),
    ]
    
    nombres_revisador_choices = [
    ('Gerente de Calidad', 'Gerente de Calidad'),
    ('Ingeniero de Calidad', 'Ingeniero de Calidad'),
    ('Ingeniero de Sistemas de Gestión', 'Ingeniero de Sistemas de Gestión'),
    ('Supervisor de Producción', 'Supervisor de Producción'),
    ]
    
    ESTADO_CHOICES = [
        ('HABILITADO','HABILITADO'),
        ('INHABILITADO',('INHABILITADO'))
    ]



    nombre = models.CharField(max_length=100, choices = nombres_plantillas_choices)
    archivo = models.FileField(upload_to='rutas/', max_length=500, null= True,blank=True)
    autor = models.CharField(max_length=50, choices =  nombres_autor_choices)
    revisador = models.CharField(max_length=50, choices =  nombres_revisador_choices)
    aprobador = models.CharField(max_length=50, choices =  nombres_aprobado_choices)
    codigo = models.CharField(max_length=20)
    revision_actual = models.IntegerField()
    tipo_de_area = models.CharField(max_length=20,null = True)
    estado = models.CharField(max_length=20, choices = ESTADO_CHOICES)
    tipo_liberacion = models.ForeignKey(Liberacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre



class DocumentoBloqueado(models.Model):
    nomenclatura = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)
    id_responsable = models.ForeignKey(User, on_delete=models.CASCADE)  # Corregido para usar ForeignKey
    estado = models.CharField(max_length=100)
    codigo_identificacion = models.CharField(max_length=200)
    intentos_descarga = models.IntegerField(default=0)
    
class Documento(models.Model):
    REVISION_NUMEROS_CHOICES = [(f"{i:02d}", f"{i:02d}") for i in range(101)]
    
    # Relaciones ForeignKey con otros modelos
    id_plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)
    id_linea = models.ForeignKey(Linea, on_delete=models.CASCADE)
    id_responsable = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos_responsables')
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    revisador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos_revisados')
    aprobador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos_aprobados')
    estado = models.CharField(max_length=50, default='APROBADO')
    fecha_finalizacion = models.DateTimeField(default=timezone.now, null=True, blank=True)
    revision_de_plantilla = models.CharField(null=True, max_length=50, choices=REVISION_NUMEROS_CHOICES)
    revision_documento = models.CharField(null=True, max_length=50, choices=REVISION_NUMEROS_CHOICES)
    consecutivo = models.CharField(max_length=50, choices=REVISION_NUMEROS_CHOICES)
    extension = models.CharField(max_length=10, default= '.docx')
    comentarios = models.TextField()
    
    
    @classmethod
    def CD_Firma_Documento_Pendiente(cls, id_interesado):
        return cls.objects.filter(
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
    

    def __str__(self):
        return self.nombre
    
    


    
    
class FormatosPermitidos(models.Model):
    
    extension_documentos_choices = [
    ('.ppt', '.ppt (PowerPoint)'),
    ('.pptx', '.pptx (PowerPoint)'),
    ('.xls', '.xls (Excel)'),
    ('.xlsx', '.xlsx (Excel)'),
    ('.doc', '.doc (Word)'),
    ('.docx', '.docx (Word)'),
    ('.pdf', '.pdf (PDF)'),
  ]
    Tipo_de_documento = models.CharField(max_length=50)
    Extencion = models.CharField( max_length=50, choices = extension_documentos_choices)
    
    def __str__(self):
        return self.Tipo_de_documento + self.Extencion
    
    
    
# Modelo para Historial
class Historial(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    id_responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    accion = models.TextField()



