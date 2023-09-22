import datetime
from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .models import *


# функция отправки уведомлений подписчикам на почту о новом объявлении в любимой категории
def subscribers_send_mails(pk, headline, subscribers_emails):
    # указываем какой шаблон брать за основу и преобразовываем его в строку для отправки подписчику
    html_context = render_to_string(
        'email/post_add_email.html',
        {
            'link': f'{settings.SITE_URL}/posts/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        # тема письма
        subject = post_title,
        # тело пустое, потому что мы используем шаблон
        body='',
        # адрес отправителя
        from_email=settings.DEFAULT_FROM_EMAIL,
        # список адресатов
        to=subscribers_emails,
    )

    msg.attach_alternative(html_context, 'text/html')
    msg.send(fail_silently=False)


# функция отправки на почту автору объявления уведомления
# о том, что у него есть новый комментарий
def post_reply_send_mail(pk, email):
    # указываем какой шаблон брать за основу и преобразовываем его в строку для отправки подписчику
    html_context = render_to_string(
        'email/reply_add_email.html',
        {
            'link': f'{settings.SITE_URL}/ads/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        # тема письма
        subject='Новый отклик',
        # тело пустое, потому что мы используем шаблон
        body='',
        # адрес отправителя
        from_email=settings.DEFAULT_FROM_EMAIL,
        # список адресатов
        to=email,
    )

    msg.attach_alternative(html_context, 'text/html')
    msg.send(fail_silently=False)


# функция отправки на почту автору оклика уведомления о том, что его отклик принят
def reply_author_send_mail(pk, email):
    # указываем какой шаблон брать за основу и преобразовываем его в строку для отправки подписчику
    html_context = render_to_string(
        'email/reply_author_email.html',
        {
            'link': f'{settings.SITE_URL}/ads/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        # тема письма
        subject='Отклик принят',
        # тело пустое, потому что мы используем шаблон
        body='',
        # адрес отправителя
        from_email=settings.DEFAULT_FROM_EMAIL,
        # список адресатов
        to=email,
    )

    msg.attach_alternative(html_context, 'text/html')
    msg.send(fail_silently=False)


# задача, которая уведомляет о новом объявлении в любимом разделе
@shared_task
def posts_add_notification(pk):
    post = Post.objects.get(id=pk)
    category = post.category
    subscribers = []
    subscribers_emails = []
    subscribers += category.subscribers.all()

    for s in subscribers:
        subscribers_emails.append(s.email)

    subscribers_send_mails(post.pk, post.post_title, subscribers_emails)


# задача, которая уведомляет о новом отклике на объявление
@shared_task
def post_reply_notification(pk):
    reply = Post.objects.get(id=pk)
    post = reply.post
    post_author_email = [post.author.email]
    post_reply_send_mail(post.pk, post_author_email)


# задача, которая уведомляет о принятом отклике
@shared_task
def reply_approve_notification(pk):
    reply = Reply.objects.get(id=pk)
    post = reply.post
    reply_author_email = [reply.author.email]
    reply_author_send_mail(post.pk, reply_author_email)


# задача по еженедельной отправке сообщения подписчикам со списком новых объявлений за неделю
# из категорий, на которые они подписаны
@shared_task
def my_job():
    #  Your job processing logic here...
    today = datetime.datetime.now()
    week_ago = today - datetime.timedelta(days=7)
    ads = Post.objects.filter(created_at__gte=week_ago)
    categories = set(ads.values_list('category__name', flat=True))
    subscribers_emails = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'email/weekly_announcement.html',
        {
            'link': settings.SITE_URL,
            'ads': ads
        }
    )
    msg = EmailMultiAlternatives(
        subject='Объявления за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)