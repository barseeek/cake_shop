from django.db import models


EXTRA_PRICES = {
    'levels': {'1': 400, '2': 750, '3': 1100, },
    'shapes': {'square': 600, 'circle': 400, 'rectangle': 1000, },
    'toppings': {
        'no_topping': 0,
        'white_sauce': 200,
        'caramel_syrup': 180,
        'maple_syrup': 200,
        'strawberry_syrup': 300,
        'blueberry_syrup': 350,
        'milk_chocolate': 200,
    },
    'berries': {
        'no_berries': 0,
        'blackberry': 400,
        'raspberry': 300,
        'blueberry': 450,
        'strawberry': 500,
    },
    'decor': {
        'no_decor': 0,
        'pistachio': 300,
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
    username = models.CharField(
        'Имя пользователя в Telegram',
        max_length=100,
        unique=True,
    )
    address = models.TextField('Адрес')

    class Meta:
        ordering = ['id']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.username


class CakeQuerySet(models.QuerySet):
    """Пользовательский класс QuerySet для модели Cake."""
    def get_price(self):
        """Вычислить и записать стоимость торта."""
        cake = self.first()
        price = (
            EXTRA_PRICES['levels'][str(cake.levels_number)] + 
            EXTRA_PRICES['shapes'][cake.shape] +
            EXTRA_PRICES['toppings'][cake.topping] +
            EXTRA_PRICES['berries'][cake.berries] +
            EXTRA_PRICES['decor'][cake.decor]
        )  
        self.update(price=price)


class Cake(models.Model):
    """Модель торта, собранного самостоятельно."""
    LEVEL_CHOICES = [(1, '1 уровень'), (2, '2 уровня'), (3, '3 уровня'),]
    SHAPE_CHOICES = [
        ('square', 'квадрат'),
        ('circle', 'круг'),
        ('rectangle', 'прямоугольник'),
    ]
    TOPPING_CHOICES = [
        ('no_topping', 'без топпинга'),
        ('white_sauce', 'белый соус'),
        ('caramel_syrup', 'карамельный сироп'),
        ('maple_syrup', 'кленовый сироп'),
        ('strawberry_syrup', 'клубничный сироп'),
        ('blueberry_syrup', 'черничный сироп'),
        ('milk_chocolate', 'молочный шоколад'),
    ]
    BERRIES_CHOICES = [
        ('no_berries', 'без ягод'),
        ('blackberry', 'ежевика'),
        ('raspberries', 'малина'),
        ('blueberry', 'голубика'),
        ('strawberry', 'клубника'),
    ]
    DECOR_CHOICES = [
        ('no_decor', 'без декора'),
        ('pistachio', 'фисташки'),
        ('meringue', 'безе'),
        ('hazelnut', 'фундук'),
        ('pecan', 'пекан'),
        ('marshmallow', 'маршмеллоу'),
        ('marzipan', 'марципан'),
    ]
    
    title = models.CharField(
        'Название',
        max_length=100,
        default='Пользовательский торт',
    )
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
    price = models.FloatField('Цена', blank=True, null=True)
    is_base = models.BooleanField('Стандартный торт', default=False)
    objects = CakeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Торт'
        verbose_name_plural = 'Торты'

    def __str__(self):
        return f'{self.title}'


class OrderQuerySet(models.QuerySet):
    """Пользовательский класс QuerySet для модели Order."""
    def get_total_price(self):
        """Вычислить и записать полную стоимость заказа."""
        order = self.first()
        print(order)
        total_price = order.cake.price
        if order.inscription:
            total_price += EXTRA_PRICES['inscription']
        if order.fast_delivery:
            total_price *= EXTRA_PRICES['express_coefficient']
        print(total_price)
        self.update(total_price=total_price)
        order.total_price = total_price
        order.save()
        print(order.total_price)


class Order(models.Model):
    """Модель заказа."""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Клиент',
    )
    comment = models.TextField('Комментарий', blank=True, null=True,)
    date = models.DateField('Дата доставки')
    time = models.CharField('Время доставки', max_length=50)
    cake = models.ForeignKey(
        Cake,
        verbose_name='Торт',
        related_name='orders',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    inscription = models.CharField('Надпись', max_length=200, blank=True, null=True)
    total_price = models.FloatField('Конечная цена', blank=True, null=True)
    fast_delivery = models.BooleanField('Быстрая доставка', default=False)
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ клиента {self.client}'


class Advertising(models.Model):
    """Модель рекламы."""
    url = models.URLField('Ссылка', blank=True)
    text = models.TextField('Текст рекламы')
    responses = models.IntegerField(
        'Количество откликов',
        null=True,
        blank=True,
        default=0,
    )

    class Meta:
        verbose_name = 'Реклама'
        verbose_name_plural = 'Реклама'
