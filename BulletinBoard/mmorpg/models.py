from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

Tanks = 'TNK'
Healers = 'HEA'
DD = 'DD'
Merchants = 'MCH'
Guildmasters = 'GMA'
Questgivers = 'QMA'
Blacksmiths = 'BLM'
Leatherworkers = 'LWK'
Potionmakers = 'PMK'
Spellmasters = 'SMA'

CATEGORY = [
    (Tanks, 'Танки'),
    (Healers, 'Хилы'),
    (DD, 'ДД'),
    (Merchants, 'Торговцы'),
    (Guildmasters, 'Гилдмастеры'),
    (Questgivers, 'Квестгиверы'),
    (Blacksmiths, 'Кузнецы'),
    (Leatherworkers, 'Кожевники'),
    (Potionmakers, 'Зельевары'),
    (Spellmasters, 'Мастера заклинаний'),
]


class Post(models.Model):
    post_title = models.CharField(max_length=255)
    post_text = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=3, choices=CATEGORY, default=Tanks)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('post', args=[str(self.id)])

    def __str__(self):
        return self.post_title


class Reply(models.Model):
    reply_text = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    accepted = models.BooleanField(default=False)

    def send_notification_email(self):
        subject = 'Отклик на ваше объявление'
        message = f'Здравствуйте!\n\nНа ваше объявление "{self.post}" появился новый отклик.\n\nС уважением,\nВаш сайт.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.post.user.email]

        send_mail(subject, message, from_email, recipient_list)

    def send_accepted_email(self):
        subject = 'Ваш отклик принят'
        message = f'Здравствуйте!\n\nВаш отклик "{self.reply_text[:15]}" принят.\n\nС уважением,\nВаш сайт.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.user.email]

        send_mail(subject, message, from_email, recipient_list)

    def get_absolute_url(self):
        return reverse('posts')

    def __str__(self):
        return self.reply_text