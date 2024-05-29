from django.contrib.auth.models import User  # Importa el modelo de usuario predeterminado de Django
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views import generic
from django.contrib import messages
from Usuarios.models import PerfilUsuario




class LoginView(generic.View):
    def get(self, request):
        # Verifica si el usuario ya está autenticado
        if request.user.is_authenticated:
            return redirect('home')  # Redirige a la página de inicio si ya está autenticado
        return render(request, 'login/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Busca un usuario con el correo electrónico proporcionado
        user = User.objects.filter(email=email).first()
        if user:
            # Autentica al usuario con el correo electrónico y la contraseña proporcionados
            user = authenticate(request, username=user.username, password=password)
            if user:
                # Verifica si el usuario está activo en PerfilUsuario
                perfil_usuario = PerfilUsuario.objects.filter(user=user, estado='ACTIVO').first()
                if perfil_usuario:
                    auth_login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Tu cuenta no está activa. Contacta al administrador.')
            else:
                messages.error(request, 'Correo electrónico o contraseña inválidos')
        else:
            messages.error(request, 'No se encontró una cuenta con ese correo electrónico')

        return render(request, 'login/login.html', {})


@login_required
def home(request):
    print("inicie sesion")
    return render(request, 'home.html')

def logout_view(request):
    print("Cerre session")
    logout(request)
    return redirect('login')