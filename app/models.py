from django.db import models


EXTRA_PRICES = {
    'levels': {1: 400, 2: 750, 3: 1100, },
    'shapes': {'square': 600, 'circle': 400, 'rectangle': 1000, },
    'toppings': {
        'nothing': 0,
        'white_souce': 200,
        'caramel syrup': 180,
        'maple syrup': 200,
        'strawberry syrup': 300,
        'blueberry syrup': 350,
        'milk chocolate': 200,
    },
    'berries': {
        'blackberry': 400,
        'raspberries': 300,
        'blueberry': 450,
        'strawberry': 500,
    },
    'decor': {
        'pistachios': 300,
        'meringue': 400,
        'hazelnut': 350,
        'pecan': 300,
        'marshmallow': 200,
        'marzipan': 280,
    },
    'inscription': 500,
    'express_coefficient': 1.2,
}


class Client(models.Model):
    """Модель клиента."""
    username = models.CharField('Имя пользователя в Telegram', max_length=100)
    address = models.TextField('Адрес')

    class Meta:
        ordering = ['id']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.username


class BaseCake(models.Model):
class BaseCake(models.Model):
    """Модель торта из стандартного меню."""
    title = models.CharField('Название', max_length=100)
    inscription = models.CharField(
        'Надпись на торте', max_length=200, blank=True, null=True)
    price = models.FloatField('Цена')

    class Meta:
        ordering = ['title']
        verbose_name = 'Торт из меню'
        verbose_name_plural = 'Торты из меню'

    class Meta:
        ordering = ['title']
        verbose_name = 'Торт из меню'
        verbose_name_plural = 'Торты из меню'

    def __str__(self):
        return self.title


class CustomCake(models.Model):
    """Модель торта, собранного самостоятельно."""
    LEVEL_CHOICES = [(1, '1 уровень'), (2, '2 уровня'), (3, '3 уровня'),]
    SHAPE_CHOICES = [
        ('square', 'квадрат'),
        ('circle', 'круг'),
        ('rectangle', 'прямоугольник'),
    ]
    TOPPING_CHOICES = [
        ('nothing', 'без топпинга'),
        ('white_souce', 'белый соус'),
        ('caramel syrup', 'карамельный сироп'),
        ('maple syrup', 'кленовый сироп'),
        ('strawberry syrup', 'клубничный сироп'),
        ('blueberry syrup', 'черничный сироп'),
        ('milk chocolate', 'молочный шоколад'),
    ]
    BERRIES_CHOICES = [
        ('blackberry', 'ежевика'),
        ('raspberries', 'малина'),
        ('blueberry', 'голубика'),
        ('strawberry', 'клубника'),
    ]
    DECOR_CHOICES = [
        ('pistachios', 'фисташки'),
        ('meringue', 'безе'),
        ('hazelnut', 'фундук'),
        ('pecan', 'пекан'),
        ('marshmallow', 'маршмеллоу'),
        ('marzipan', 'марципан'),
    ]

    levels_number = models.SmallIntegerField(
        'Количество уровней',
        choices=LEVEL_CHOICES,
    )
    shape = models.CharField(
        'Форма',
        max_length=50,
        choices=SHAPE_CHOICES,
        )
    topping = models.CharField(
        'Топпинг',
        max_length=50,
        choices=TOPPING_CHOICES,
    )
    berries = models.CharField(
        'Ягоды',
        max_length=50,
        choices=BERRIES_CHOICES,
        blank=True,
        null=True,
    )
    decor = models.CharField(
        'Декор',
        max_length=50,
        choices=DECOR_CHOICES,
        blank=True,
        null=True,
    )
    inscription = models.CharField(
        'Надпись',
        max_length=200,
        blank=True,
        null=True,
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='custom_cakes',
        verbose_name='Заказ',
        blank=True,
        null=True,
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='custom_cakes',
        verbose_name='Клиент'
    )
    price = models.FloatField('Цена')

    class Meta:
        verbose_name = 'Кастомный торт'
        verbose_name_plural = 'Кастомные торты'

    def __str__(self):
        return f'Кастомный торт клиента {self.client}'


class Order(models.Model):
    """Модель заказа."""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Клиент',
    )
    comment = models.TextField('Комментарий', blank=True, null=True,)
    date_time = models.DateTimeField('Дата и время доставки')
    base_cakes = models.ManyToManyField(
        BaseCake,
        through='OrderBaseCake',
        verbose_name='Торты из меню',
        blank=True,
        # null=True,
        related_name='orders',
    )
    total_price = models.FloatField('Конечная цена')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Кастомный торт клиента {self.client}'


class OrderBaseCake(models.Model):
    """Модель тортов из меню в заказе."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ')
    base_cake = models.ForeignKey(
        BaseCake,
        on_delete=models.CASCADE,
        verbose_name='Торт')
    amount = models.IntegerField('Количество тортов в заказе')

    class Meta:
        verbose_name = 'Торт из меню в заказе'
        verbose_name_plural = 'Торты из меню в заказе'


class Advertising(models.Model):
    """Модель рекламы."""
    url = models.URLField('Ссылка')
    text = models.TextField('Текст рекламы')
    responses = models.IntegerField('Количество откликов')

    class Meta:
        verbose_name = 'Реклама'
        verbose_name_plural = 'Реклама'
