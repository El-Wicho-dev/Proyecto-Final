from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_correo_ordinario(to_email,subject,factory_name, title, message, link):
    context = {
        'subject': subject,
        'factory_name': factory_name,
        'title': title,
        'message': message,
        'link': link
    }

    # Rendering HTML content to string
    email_html_message = render_to_string('email.html', context)

    # Creating email
    email = EmailMessage(
        subject=subject,
        body=email_html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
    )
    email.content_subtype = 'html'  # Main content is now text/html
    email.send()
    





