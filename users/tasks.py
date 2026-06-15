from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta

from users.models import CustomUser

@shared_task
def send_welcome_message(emaill):

    print(f'Добро пожаловать, {emaill}!')


@shared_task
def delete_inactive_users():

    users = CustomUser.objects.filter(
        is_active=False,
        created_at__lte=timezone.now() - timedelta(days=7)
    )

    count = users.count()

    users.delite()

    print(f'Удалено {count} неактивных пользователей')


@shared_task
def send_confirmation_email(email, code):

    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения: {code}',
        from_email='admin@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )