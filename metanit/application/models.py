from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.utils import timezone
# Create your models here.


class TypeContent(models.Model):
    title_type = models.CharField(
        max_length=50,
        verbose_name="Тип контента",
        help_text="Введите название контента",
    )

    def __str__(self):
        return self.title_type


class Creator(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Имя издателя",
        help_text="Введите имя издателя",
    )
    summery = models.TextField(
        max_length=2000,
        verbose_name="Описание издателя",
        help_text="Введите описание издателя",
    )

    def __str__(self):
        return self.name


class ReasonsToBuy(models.Model):
    summery = models.TextField(
        max_length=2000,
        verbose_name="Описание причины",
        help_text="Введите описание причины",
    )

    def __str__(self):
        return self.summery


class Content(models.Model):
    image = models.ImageField(
        verbose_name="Картинка контента",
        help_text="Вставте картинку контента",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Название контента",
        help_text="Введите название контента",
    )
    summery = models.TextField(
        max_length=1000,
        verbose_name="Описание контента",
        help_text="Введите описание контента",
    )
    creator = models.ManyToManyField(
        Creator,
        verbose_name="Создатель контента",
        help_text="Введите создателя контента",
    )
    evaluation = models.FloatField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1.0, message='Оценка не может быть меньше 1.0'),
            MaxValueValidator(10.0, message='Оценка не может быть больше 10.0')
        ],
        help_text='Оценка от 1.0 до 10.0'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reasons_to_buy = models.ManyToManyField(
        ReasonsToBuy,
        verbose_name="Причины опробовать данный контент",
        help_text="Введите причины опробовать данный контент",
    )
    type_content = models.ForeignKey(
        TypeContent,
        on_delete=models.CASCADE,
        verbose_name="Типы контента",
        help_text="Введите типы контента",
    )

    def __str__(self):
        return self.title


class User(AbstractUser):
    content_like = models.ManyToManyField(
        Content,
        verbose_name="Контент который нравится пользователю",
        help_text="Введите контент который нравится пользователю",
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='user',
    )

    def clear_sessions(self):
        """Очищает все сессии пользователя"""
        Session.objects.filter(
            expire_date__gte=timezone.now(),
            session_data__contains=str(self.id)
        ).delete()

    def logout_all_sessions(self):
        """Выход из всех сессий пользователя"""
        self.clear_sessions()
        return True

    def __str__(self):
        return self.username


class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True
    )
    viewed = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    time_spent = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'content')

    def __str__(self):
        return self.user.id