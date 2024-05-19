from django.contrib import admin
from .models import Plantilla,Liberacion,Documento,FormatosPermitidos

# Register your models here.

admin.site.register(Plantilla)
admin.site.register(Liberacion)
admin.site.register(Documento)



class FormatosPermitidosAdmin(admin.ModelAdmin):
    list_display = ('Tipo_de_documento', 'Extencion')  # Agregamos 'tipo_documento', 'extension' y 'full_name' a la lista de campos a mostrar


admin.site.register(FormatosPermitidos, FormatosPermitidosAdmin)