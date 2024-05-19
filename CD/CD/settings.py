

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s(#cd$+8mz0uqcqks)*n@u!2csr$&zelixsfj%@7e1!ma*-psi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



# Application definition


BASE_APPS =[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'aprobar_entrenamiento',
    'aprobar_documento',
    'asignar_entrenamiento',
    'descargar_editable',
    'Entrenamiento',
    'liberar_documento',
    'matriz_entrenamiento',
    'home',
    'agregar_documento',
    'realizar_entrenamiento',
    'django_seed',
    'django_extensions',
    'solicitar_liberacion',
    'Documentos',
    'Usuarios',
    'solicitar_firmas',
    'bloquear_documento',
    'eliminar_documento',
    'bitacora',
    'actualizar_documento',
    'actualizar_nomenclatura',
    'actualizar_puestos'

]

THIRD_APPS = [
    'rest_framework',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CD.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CD.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Control_de_Documentos',
        'USER': 'root',
        'PASSWORD': '0109',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


MEDIA_URL = '/media/'
MEDIA_URL2 = 'media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
TEMP_OUTPUT_DIR = os.path.join(MEDIA_ROOT, 'temp')



# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

X_FRAME_OPTIONS = 'SAMEORIGIN'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from django.contrib.messages import constants as messages

#Estos Alerta son de boootrap basado  a las console de messeges de django 
"""
MESSAGE_TAGS = {
    messages.DEBUG: 'dark',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
"""

#Estos Alerta son de sweetalert console de messeges de django 

MESSAGE_TAGS = {
    messages.DEBUG: 'question',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}



# settings.py

#Configuracion para mandar correos

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'umtrack24@gmail.com'
EMAIL_HOST_PASSWORD = 'nombxrwxsoiyfsgf'



RUTA_PRINCIPAL = '/media/plantillas/'
RUTA_EDITABLES = '/media/rutas/'