from django.db import models
from django.contrib.auth.models import User
from Documentos.models import Documento
from Usuarios.models import UsuarioPuesto,Puesto,UnidadNegocio
from django.utils import timezone  # Importa esto para manejar correctamente la zona horaria

# Modelo para Entrenamientos
class Entrenamiento(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.FloatField(blank= True,null=True)
    fecha = models.DateTimeField(blank=True,null=True)
    estado = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return f"Entrenamiento para Usuario: {self.id_usuario.first_name} {self.id_usuario.last_name} con el documento {self.id_documento.nombre}"

# Modelo para Firmas
class Firma(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='firmas')
    id_liberador = models.ForeignKey(User,on_delete=models.CASCADE, null=True,default=None)  # Considerar cambiar a ForeignKey si corresponde
    firma = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"Firma para Documento: {self.id_documento}"



# Modelo para Entrenamiento_Puesto_Nomenclatura
class EntrenamientoPuestoNomenclatura(models.Model):
    id_puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField()
    nomenclatura = models.CharField(max_length=100)
    id_unidad_negocio = models.ForeignKey(UnidadNegocio, on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return f"La nomenclautura Documento: {self.nomenclatura}"