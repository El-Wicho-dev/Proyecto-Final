from django.db import models

"""""
# Modelo para Usuarios
class Usuario(models.Model):
    no_empleado = models.CharField(max_length=20)
    nombre = models.CharField(max_length=70)
    apellido = models.CharField(max_length=70)
    correo = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=100)  # Cambiado de 'contraseña' a 'contrasena' para evitar problemas de codificación
    estado = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Modelo para Documentos Bloqueados
class DocumentoBloqueado(models.Model):
    nomenclatura = models.CharField(max_length=100)
    fecha = models.DateField()
    id_responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Corregido para usar ForeignKey
    estado = models.CharField(max_length=100)
    codigo_identificacion = models.CharField(max_length=200)
    intentos_descarga = models.IntegerField()

# Modelo para Liberaciones
class Liberacion(models.Model):
    liberacion = models.IntegerField()
    descripcion = models.TextField()

    def __str__(self):
        return f"Liberacion {self.liberacion}"

# Modelo para Plantillas
class Plantilla(models.Model):
    nombre = models.CharField(max_length=100)
    archivo = models.TextField()
    autor = models.CharField(max_length=100)
    revisador = models.CharField(max_length=100)
    aprobador = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    revision_actual = models.IntegerField()
    estado = models.CharField(max_length=20)
    tipo_liberacion = models.ForeignKey(Liberacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Linea(models.Model):
    nombre_linea = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre_linea

class Documento(models.Model):
    nombre = models.CharField(max_length=200)
    id_plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)  # Corregido para usar ForeignKey correctamente
    id_linea = models.ForeignKey(Linea, on_delete=models.CASCADE)
    id_responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    revision = models.IntegerField()
    aprobador = models.IntegerField()  # Asumiendo que es un ID, pero podría necesitar cambiar a ForeignKey
    estado = models.CharField(max_length=50)
    fecha_finalizacion = models.DateTimeField()
    consecutivo = models.IntegerField()
    extension = models.CharField(max_length=10)
    revision_plantilla = models.IntegerField()
    comentarios = models.TextField()

    def __str__(self):
        return self.nombre

# Modelo para Áreas
class Area(models.Model):
    area = models.CharField(max_length=100)

    def __str__(self):
        return self.area

# Modelo para Departamentos
class Departamento(models.Model):
    departamento = models.CharField(max_length=30)
    id_area = models.ForeignKey(Area, on_delete=models.CASCADE)  # Corregido para usar ForeignKey correctamente

    def __str__(self):
        return self.departamento

# Modelo para Puestos
class Puesto(models.Model):
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)  # Corregido para usar ForeignKey correctamente
    descripcion_general = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20)
    por_unidad_negocio = models.BooleanField()

    def __str__(self):
        return self.descripcion_general  # Cambiado para evitar un error si 'departamento' no es un campo de 'Puesto'

# Modelo para UsuarioPuestos
class UsuarioPuesto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('usuario', 'puesto'),)

# Modelo para Historial
class Historial(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    id_responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    accion = models.TextField()

    def __str__(self):
        return f"Documento {self.id_documento.nombre} Acción: {self.accion}"

# Modelo para Entrenamientos
class Entrenamiento(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calificacion = models.FloatField()
    fecha = models.DateTimeField()

    def __str__(self):
        return f"Entrenamiento para Usuario: {self.id_usuario.nombre}"

# Modelo para Firmas
class Firma(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    liberador = models.IntegerField()  # Considerar cambiar a ForeignKey si corresponde
    firma = models.DateTimeField()

    def __str__(self):
        return f"Firma para Documento: {self.id_documento.nombre}"



# Modelo para Unidades_Negocio
class UnidadNegocio(models.Model):
    unidad_negocio = models.CharField(max_length=100)
    gerente_Calidad = models.IntegerField()  # Considerar cambiar a ForeignKey si corresponde
    gerente_ingenieria = models.IntegerField()  # Considerar cambiar a ForeignKey si corresponde
    gerente_produccion = models.IntegerField()  # Considerar cambiar a ForeignKey si corresponde

# Modelo para Entrenamiento_Puesto_Nomenclatura
class EntrenamientoPuestoNomenclatura(models.Model):
    id_puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField()
    nomenclatura = models.CharField(max_length=100)
    id_unidad_negocio = models.ForeignKey(UnidadNegocio, on_delete=models.CASCADE)

class FormatosPermitidos(models.Model):
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    Tipo_de_documento = models.CharField(max_length=50)
    Extencion = models.CharField( max_length=50)
    
    def __str__(self):
        return self.Tipo_de_documento
    
"""