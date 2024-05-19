from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


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
    
