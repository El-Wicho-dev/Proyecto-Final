from django.contrib import admin
from .models import Departamento,Area,Linea
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario, UsuarioPuesto, Puesto,UnidadNegocio
from .forms import PerfilUsuarioForm, PuestoForm  # Asume que tienes formularios para estos

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    form = PerfilUsuarioForm

class UsuarioPuestoInline(admin.StackedInline):
    model = UsuarioPuesto
    can_delete = False
    extra = 1  # Define cuántos formularios de puestos mostrar por defecto

# Extiende el UserAdmin original para incluir el inline de PerfilUsuario
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline, UsuarioPuestoInline)

# Re-registra el modelo User con el UserAdmin personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Departamento)
admin.site.register(Area)
admin.site.register(Linea)
admin.site.register(UnidadNegocio)

class PuestoAdmin(admin.ModelAdmin):
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'descripcion_general':
            kwargs['queryset'] = Puesto.objects.values('descripcion_general').distinct()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

admin.site.register(Puesto, PuestoAdmin)

