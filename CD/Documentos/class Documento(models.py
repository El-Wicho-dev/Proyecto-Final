from django.db import models
from Usuarios.models import User,Linea
from time import timezone



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
        ('PROCEDIMIENTO','PROCEDIMIENTO'),
        ('AYUDA VISUAL','AYUDA VISUAL'),
        ('PLANTILLA','PLANTILLA'),
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
    fecha_finalizacion = models.DateTimeField(default=timezone.now)
    revision_de_plantilla = models.CharField(null=True, max_length=50, choices=REVISION_NUMEROS_CHOICES)
    revision_documento = models.CharField(null=True, max_length=50, choices=REVISION_NUMEROS_CHOICES)
    consecutivo = models.CharField(max_length=50, choices=REVISION_NUMEROS_CHOICES)
    extension = models.CharField(max_length=10, default= '.docx')
    comentarios = models.TextField(default='Documento dado de alta manualmente')
    
    
# Modelo para Áreas
class Area(models.Model):
    
    areas_choices = [
        ('Area 1','Area 1'),
        ('Area 2','Area 2'),
        ('Area 3','Area 3'),
        ('Area 4','Area 4'),
        ('Departamento','Departamento'),
    ]
    
    
    area = models.CharField(max_length=100, choices = areas_choices)

    def __str__(self):
        return self.area
    
    
    
class Linea(models.Model):
    nombre_linea = models.CharField(max_length=50)
    codigo_linea = models.CharField(max_length=50, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.nombre_linea
    
    
    
    
    


class DocumentoBloqueado(models.Model):
    nomenclatura = models.CharField(max_length=100)
    fecha = models.DateField()
    id_responsable = models.ForeignKey(User, on_delete=models.CASCADE)  # Corregido para usar ForeignKey
    estado = models.CharField(max_length=100)
    codigo_identificacion = models.CharField(max_length=200)
    intentos_descarga = models.IntegerField()