from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import PerfilUsuarioForm, PuestoForm, CustomUserCreationForm
from .models import UsuarioPuesto, User,PerfilUsuario,Puesto
from django.contrib import messages


def adduser(request):
    template_name = "users/adduser.html"
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        perfil_usuario_form = PerfilUsuarioForm(request.POST)

        if user_form.is_valid():
            new_user = user_form.save()
            # La señal post_save asociada a User debería crear el PerfilUsuario automáticamente
            
            # Ahora que el usuario está creado (y su perfil ha sido creado por la señal),
            # podemos actualizar el perfil con información adicional desde perfil_usuario_form
            if perfil_usuario_form.is_valid():
                perfil_usuario = PerfilUsuario.objects.get(user=new_user)  # Obtener el perfil recién creado
                perfil_usuario_form = PerfilUsuarioForm(request.POST, instance=perfil_usuario)  # Vincular el formulario con la instancia existente
                perfil_usuario_form.save()  # Guardar la información adicional en el perfil
                
            
            # Redirige al paso de creación del perfil y puesto con el ID del nuevo usuario
            return redirect('add_profile', user_id=new_user.id)
    else:
        perfil_usuario_form = PerfilUsuarioForm()
        user_form = CustomUserCreationForm()

    context = {
        'user_form': user_form,
        'perfil_usuario_form': perfil_usuario_form,
    }
    return render(request, template_name, context)

def add_profile(request, user_id):
    template_name = "users/add_profile.html"  # Asume que tienes una plantilla separada para esto
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        puesto_form = PuestoForm(request.POST)
        if  puesto_form.is_valid():
            
            puesto = puesto_form.save()
            UsuarioPuesto.objects.create(usuario=user, puesto=puesto)
            messages.success(request,"Se dio Alta el Usuario")
            return redirect('home')  # o donde quieras redirigir después
    else:
        puesto_form = PuestoForm()

    context = {
        'puesto_form': puesto_form,
        'user': user,
    }
    return render(request, template_name, context)




def blockuser(request):
    template_name = "users/blockuser.html"
    puesto_info = None  # Inicializar con None
    usuario_info = None  # Variable para almacenar información del usuario
    no_empleado = request.POST.get('no_empleado', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'search':
            if not no_empleado:  # Verificar si el campo está vacío después de quitar espacios
                messages.error(request, 'Favor de ingresar un número de empleado.')
            else:
                try:
                    perfil_usuario = PerfilUsuario.objects.get(no_empleado=no_empleado)
                    usuario_info = perfil_usuario.user  # Acceder al objeto User asociado
                    try:
                        usuario_puesto = UsuarioPuesto.objects.filter(usuario=perfil_usuario.user).first()
                        if usuario_puesto:
                            puesto_info = usuario_puesto.puesto
                        else:
                            # Si no hay información de puesto para este usuario
                            messages.error(request, 'No existe información de puesto para este empleado.')
                    except UsuarioPuesto.DoesNotExist:
                        # Aunque este bloque no es estrictamente necesario porque ya estás manejando la posibilidad de que no haya puesto con el 'if' anterior
                        messages.error(request, 'No existe información de puesto para este empleado.')
                except PerfilUsuario.DoesNotExist:
                    # Aquí es donde manejas el error cuando no encuentras un PerfilUsuario
                    messages.error(request, 'No existe este empleado.')

        elif action == 'block':
            user_id = request.POST.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    try:
                        perfil_usuario = PerfilUsuario.objects.get(user=user)
                        perfil_usuario.estado = "INACTIVO"
                        perfil_usuario.save()
                        messages.success(request, 'El usuario ha sido bloqueado.')
                    except PerfilUsuario.DoesNotExist:
                        messages.error(request, 'No existe este empleado.')
                except User.DoesNotExist:
                    # Manejar la situación para un User que no existe
                    messages.error(request, 'No existe este empleado.')

    context = {
        'perfil_usuario_form': PerfilUsuarioForm(),
        'puesto_info': puesto_info,
        'no_empleado': no_empleado,  # Añadir no_empleado al contexto
        'usuario_info': usuario_info,  # Agregar usuario_info al contexto


    }

    return render(request, template_name, context)



