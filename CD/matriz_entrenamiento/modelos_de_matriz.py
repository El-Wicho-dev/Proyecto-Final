from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


# Create your models here.


# Modelo para Usuarios
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Falta la relación con el User
    no_empleado = models.CharField(max_length=20)
    estado = models.CharField(max_length=10, default = "ACTIVO")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

# Señal para crear o actualizar automáticamente el perfil del usuario o mejor conocido como trig
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)
    else:
        instance.perfilusuario.save()

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
    

# Modelo para Departamentos
class Departamento(models.Model):
    
    departamentos_choices = [
        ('Calidad','Calidad'),
        ('Produccion','Produccion'),
        ('Almacen','Almacen'),
        ('Planeacion','Planeacion'),
        ('Entrenamiento','Entrenamiento'),

    ]
    
    departamento = models.CharField(max_length=200,choices = departamentos_choices)
    id_area = models.ForeignKey(Area, on_delete=models.CASCADE)  # Corregido para usar ForeignKey correctamente

    def __str__(self):
        return self.departamento


# Modelo para Unidades_Negocio
class UnidadNegocio(models.Model):
    unidad_negocio = models.CharField(max_length=100)
    gerente_Calidad = models.IntegerField(null=True,blank=True)  # Considerar cambiar a ForeignKey si corresponde
    gerente_ingenieria = models.IntegerField(null=True,blank=True)  # Considerar cambiar a ForeignKey si corresponde
    gerente_produccion = models.IntegerField(null=True,blank=True)  # Considerar cambiar a ForeignKey si corresponde
    
    def __str__(self):
        return self.unidad_negocio

# Modelo para Puestos
class Puesto(models.Model):
    tipos_choices=[
        ('DIRECTO','DIRECTO'),
        ('INDIRECTO','INDIRECTO'),
    ]
    
    Unidad_De_negocio_choices=[
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
        ('E','E'),
    ]
    
    
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)  # Corregido para usar ForeignKey correctamente
    descripcion_general = models.CharField(max_length=100)
    tipo = models.CharField(max_length=40, choices = tipos_choices)
    por_unidad_negocio = models.ForeignKey(UnidadNegocio, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion_general  # Cambiado para evitar un error si 'departamento' no es un campo de 'Puesto'
    
    
# Modelo para UsuarioPuestos
class UsuarioPuesto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('usuario', 'puesto'),)

class Linea(models.Model):
    nombre_linea = models.CharField(max_length=50)
    codigo_linea = models.CharField(max_length=50, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.nombre_linea
    

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
    
    # Modelo para Entrenamientos
class Entrenamiento(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.FloatField(blank= True,null=True)
    fecha = models.DateTimeField(blank=True,null=True)
    estado = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return f"Entrenamiento para Usuario: {self.id_usuario.first_name} {self.id_usuario.last_name} con el documento {self.id_documento.nombre}"



# Modelo para Entrenamiento_Puesto_Nomenclatura
class EntrenamientoPuestoNomenclatura(models.Model):
    id_puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField()
    nomenclatura = models.CharField(max_length=100)
    id_unidad_negocio = models.ForeignKey(UnidadNegocio, on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return f"La nomenclautura Documento: {self.nomenclatura}"