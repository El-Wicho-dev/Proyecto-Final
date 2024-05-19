from django.contrib.auth.models import User  # Importa el modelo de usuario predeterminado de Django
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views import generic


class LoginView(generic.View):
    
    def get(self, request):
        # Verifica si el usuario ya está autenticado
        if request.user.is_authenticated:
            return redirect('home')  # Redirige a la página de inicio si ya está autenticado
        # Si el usuario no está autenticado, renderiza la página de inicio de sesión
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
                auth_login(request, user)
                return redirect('home')
        # Si la autenticación falla, devuelve un error
        context = {'error': 'Correo electrónico o contraseña inválidos'}
        return render(request, 'login/login.html', context)


@login_required
def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('login')