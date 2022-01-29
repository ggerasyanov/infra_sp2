from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_year(value):
    current_year = datetime.now().year
    if -3400 > value or value > current_year:
        raise ValidationError(
            _('На данный момент нет произведений, '
              'созданных в %(value)-м году'),
            params={'value': value},
        )


def validate_score(value):
    if 0 > value or value > 10:
        raise ValidationError('Оценка должна быть от 0 до 10')


class Roles(models.Model):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_CHOICES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Аутентифицированный пользователь'),
    )


class User(AbstractUser):
    """Кастомизация модели пользователя."""
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=Roles.ROLE_CHOICES,
        default='user'
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=100,
        unique=True,
    )

    @property
    def is_admin(self):
        return self.role == Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == Roles.MODERATOR

    @property
    def is_user(self):
        return self.role == Roles.USER

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    """Описание модели категории."""
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(
        verbose_name='Название категории',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Уникальный идентификатор категории',
        max_length=50,
        unique=True,
    )


class Genre(models.Model):
    """Описание модели жанра."""
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    name = models.CharField(
        verbose_name='Название жанра',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Уникальный идентификатор жанра',
        max_length=50,
        unique=True,
    )


class Title(models.Model):
    """Описание модели произведения."""
    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    name = models.CharField(
        verbose_name='Название произведения',
        max_length=256,
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=[validate_year],
    )
    description = models.TextField(verbose_name='Описание', blank=True,)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр произведения',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.DO_NOTHING,
    )


class GenreTitle(models.Model):
    """Принадлежность произведения конкретному жанру."""
    title_id = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )
    genre_id = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.DO_NOTHING,
        related_name="titles",
    )

    class Meta:
        verbose_name = 'Жанры произведений'
        verbose_name_plural = 'Жанры произведений'


class Review(models.Model):
    """Модель для отзывов."""
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        validators=[validate_score])
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        default=timezone.now()
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]
        verbose_name = 'Отзывы'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель для комментариев к отзыву."""
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        default=timezone.now()
    )

    class Meta:
        verbose_name = 'Комментарии'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
