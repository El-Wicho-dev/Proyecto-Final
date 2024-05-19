from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, UsuarioPuesto, Area, Departamento, Puesto, Linea, UnidadNegocio



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



class CustomUserCreationForm(UserCreationForm):
    
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)


class PerfilUsuarioForm(BootstrapModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['no_empleado', 'estado']  # Agrega o elimina campos según sea necesario
        
    def __init__(self, *args, **kwargs):
        super(PerfilUsuarioForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['no_empleado'].initial = kwargs['initial'].get('no_empleado')

class UsuarioPuestoForm(BootstrapModelForm):
    class Meta:
        model = UsuarioPuesto
        fields = ['usuario', 'puesto']  # Agrega o elimina campos según sea necesario

class AreaForm(BootstrapModelForm):
    class Meta:
        model = Area
        fields = ['area']  # Agrega o elimina campos según sea necesario

class DepartamentoForm(BootstrapModelForm):
    class Meta:
        model = Departamento
        fields = ['departamento', 'id_area']  # Agrega o elimina campos según sea necesario

class PuestoForm(BootstrapModelForm):
    class Meta:
        model = Puesto
        fields = '__all__'  # Agrega o elimina campos según sea necesario

class LineaForm(BootstrapModelForm):
    class Meta:
        model = Linea
        fields = '__all__'  # Agrega o elimina campos según sea necesario
        
        # Para agregar etiquetas personalizadas a cada campo
        labels = {
            'nombre_linea': 'Linea',
        }
        # Para agregar mensajes de ayuda personalizados
        help_texts = {}

    def __init__(self, *args, **kwargs):
        super(LineaForm, self).__init__(*args, **kwargs)
        # Obtener todas las instancias de Linea y convertir sus nombres en una lista de tuplas (nombre, nombre_linea)
        opciones_linea = [(linea.nombre_linea, linea.nombre_linea) for linea in Linea.objects.all()]
        # Agregar la opción predeterminada "Select option" al principio de la lista
        opciones_linea.insert(0, ('', 'Select option'))
        # Crear un campo ChoiceField para nombre_linea con las opciones obtenidas
        self.fields['nombre_linea'] = forms.ChoiceField(choices=opciones_linea, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
        # Agregar una etiqueta al campo
        self.fields['nombre_linea'].label = 'Linea'

class UnidadNegocioForm(BootstrapModelForm):
    class Meta:
        model = UnidadNegocio
        fields = ['unidad_negocio', 'gerente_Calidad', 'gerente_ingenieria', 'gerente_produccion']  # Agrega o elimina campos según sea necesario
