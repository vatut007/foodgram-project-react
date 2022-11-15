from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

USER = 'user'
ADMIN = 'admin'

ROLES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    """User model customization class."""
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    role = models.CharField('Роль пользователя',
                            max_length=max([len(role[0]) for role in ROLES]),
                            choices=ROLES,
                            default=USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow (models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
        )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
        )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='self_following',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
