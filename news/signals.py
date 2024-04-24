from django.dispatch import receiver
from .models import PostCategory
from django.db.models.signals import m2m_changed
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def send_notifications(preview, pk, title, subscribers):
    html_content = render_to_string(
        'post_created_email.html',
        {'text':preview,
         'link' : f'http://127.0.0.1:8000/posts/{pk}'

         }
    )

    msg = EmailMultiAlternatives(
        subject=f'Статья "{title}" вышла на ресурсе!',
        body = '',
        from_email='olegnasyrov.o@yandex.ru',
        to =subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@receiver(m2m_changed, sender = PostCategory)
def notify_about_new_post(sender,instance,**kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.category.all()
        subscribers_emails = []

        for cat in categories:
            subscribers = cat.subscribers.all()
            subscribers_emails += [s.email for s in subscribers]

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers_emails)