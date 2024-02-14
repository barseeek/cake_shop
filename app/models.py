from django.db import models


class Client(models.Model):
    """Модель клиента."""
    username = models.CharField('Имя пользователя в Telegram', max_length=100)
    address = models.TextField('Адрес')

    class Meta:
        ordering = ['id']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.username


class UsualCake(models.Model):
    """Модель торта из стандартного меню."""
    title = models.CharField('Название', max_length=100)
    inscription = models.CharField(
        'Надпись на торте', max_length=200, blank=True, null=True)
    price = models.FloatField('Цена')

    def __str__(self):
        return self.title


class Advertising(models.Model):
    """Модель рекламы."""
    url = models.URLField('Ссылка')
    text = models.TextField('Текст рекламы')
    responses = models.IntegerField('Количество откликов')
    
    