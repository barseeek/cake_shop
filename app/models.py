from django.db import models


class Client(models.Model):
    """Модель клиента."""
    username = models.CharField('Имя пользователя в Telegram', max_length=100)
    address = models.TextField('Адрес')

    class Meta:
        ordering = ['id']
        verbose_name = 'Клиент'
        verbose_plural_name = 'Клиенты'

    def __str__(self):
        return self.username
