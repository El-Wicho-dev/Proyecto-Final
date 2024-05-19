from django import forms
from django.contrib.auth.models import User
from .models import Liberacion, Plantilla, Documento, FormatosPermitidos, Historial

from django.forms.widgets import (
    TextInput, PasswordInput, CheckboxInput,
    RadioSelect, Textarea, NumberInput, FileInput,
    DateInput,EmailInput,Select,SelectMultiple
)


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, DateInput):
                widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(widget, EmailInput):
                widget.attrs.update({'class': 'form-control', 'type': 'email'})
            elif isinstance(widget, TextInput):
                widget.attrs.update({'class': 'form-control'})
            elif isinstance(widget, PasswordInput):
                widget.attrs.update({'class': 'form-control', 'type': 'password'})
            elif isinstance(widget, Textarea):
                widget.attrs.update({'class': 'form-control'})
            elif isinstance(widget, NumberInput):
                widget.attrs.update({'class': 'form-control', 'type': 'number'})
            elif isinstance(widget, FileInput):
                widget.attrs.update({'class': 'form-control-file', 'type': 'file'})
            elif isinstance(widget, CheckboxInput):
                widget.attrs.update({'class': 'form-check-input', 'type': 'checkbox'})
            elif isinstance(widget, RadioSelect):
                widget.attrs.update({'class': 'form-check-input', 'type': 'radio'})
            else:
                widget.attrs.update({'class': 'form-control'})
            if hasattr(field, 'choices'):
                field.widget = forms.Select(attrs={'class': 'form-control'})
                field.choices = [('','Select option:')] + list(field.choices)[1:]
                field.empty_label = None




class LiberacionForm(BootstrapModelForm):
    class Meta:
        model = Liberacion
        fields = ['liberacion', 'descripcion']

class PlantillaForm(BootstrapModelForm):
    class Meta:
        model = Plantilla
        fields = '__all__'
    
        # Para agregar etiquetas personalizadas a cada campo
        labels = {
            'nombre' : 'Seleccione el tipo de plantilla a seleccionar',
        }
        # Para agregar mensajes de ayuda personalizados
        help_texts = {}

    def __init__(self, *args, **kwargs):
        super(PlantillaForm, self).__init__(*args, **kwargs)
    


class DocumentoForm(BootstrapModelForm):
    class Meta:
        model = Documento
        fields = '__all__'
        
        
        widgets = {
            # Puedes seguir agregando más campos y sus correspondientes widgets personalizados
            'revision_documento': forms.Select(attrs={'class': 'form-control'}), 
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': '(Sin nomenclatura, el puro nombre) Ejemplo: Hola123'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Ejemplo: número de queja de cliente, número de tarjeta','rows': '2' , 'required': 'required'}),

        }
            # Para agregar etiquetas personalizadas a cada campo
        labels = {
            'revision_documento' : 'Revisión Actual',
            'id_plantilla': 'Seleccione el tipo de Documento que va generar',
            'id_linea': 'Linea',
            'id_responsable': 'Autor',
            'revisador': 'Revisado Por',
            'aprobador': 'Aprobado Por',
            'comentarios': 'Ingrese cambio o implementacion (Obligatorio):',


        }
        # Para agregar mensajes de ayuda personalizados
        help_texts = {
                # Obtener todas las instancias de User y convertir sus nombres completos en una lista de tuplas (id, nombre_completo)
      
        }
    def __init__(self, *args, **kwargs):
        app_context = kwargs.pop('app_context', None)  # Extraer un argumento adicional que define el contexto

        super(DocumentoForm, self).__init__(*args, **kwargs)
        
        
        # Hacer explícitamente opcional los campos con valores por defecto
        self.fields['fecha_inicio'].required = False
        self.fields['fecha_finalizacion'].required = False
        self.fields['estado'].required = False
        self.fields['extension'].required = False
        self.fields['comentarios'].required = False
        
    # Personalizaciones adicionales que no se pueden hacer en la clase Meta
        usuarios = [(usuario.id, usuario.get_full_name()) for usuario in User.objects.all()]
        usuarios.insert(0, ('', 'Select option:'))
        
        # Asignar las opciones al campo autor, revisador y aprobador
        self.fields['id_responsable'].widget.choices = usuarios
        self.fields['revisador'].widget.choices = usuarios
        self.fields['aprobador'].widget.choices = usuarios    
   


        
        
        
        
        


class FormatosPermitidosForm(BootstrapModelForm):
    class Meta:
        model = FormatosPermitidos
        fields = '__all__'

class HistorialForm(BootstrapModelForm):
    class Meta:
        model = Historial
        fields = '__all__'
