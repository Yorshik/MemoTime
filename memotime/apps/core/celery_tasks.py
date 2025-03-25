import celery
import django.conf
import django.core.mail
import django.template.loader
import django.utils.html

__all__ = ()


@celery.shared_task
def send_email_task(subject, template_name, context, recipients):
    html_message = django.template.loader.render_to_string(template_name, context)
    text_message = django.utils.html.strip_tags(html_message)

    email = django.core.mail.EmailMultiAlternatives(
        subject,
        text_message,
        django.conf.settings.EMAIL_HOST_USER,
        recipients,
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
