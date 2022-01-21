from django.template import loader
from django.core.mail import EmailMessage


def send_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=[data['to_email']]
    )

    email.send()


def compose_email(user, current_sites, composed_url, email_subject, template_path=None, in_line_content=None):
    context = {
        'user': user,
        'site_name': current_sites.name,
        'composed_url': composed_url
    }

    if not in_line_content == None:
        email_body = in_line_content
    else:
        email_body = loader.render_to_string(
            template_path,
            context
        )

    email_data = {
        'email_subject': email_subject,
        'email_body': email_body,
        'to_email': user.email,
    }

    send_email(email_data)
