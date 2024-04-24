import datetime
from celery import shared_task
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import PostCategory, Post, Category


@shared_task
def new_post(pk):
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    title = post.title
    preview = post.preview()
    subscribers_emails = []
    for category in categories:
        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            if subscriber.email not in subscribers_emails:
                subscribers_emails.append(subscriber.email)

    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': preview,
            'link': f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@shared_task
def weekly_post():
    today = datetime.datetime.now()
    lastweek = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(post_time__gte=lastweek)
    categories = set(posts.values_list('category__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list("subscribers__email", flat=True))

    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,

        }
    )

    msg = EmailMultiAlternatives(
        subject="Статьи за неделю",
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()