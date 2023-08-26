from django.db import models


class Advertisement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название кампании', null=True)
    refer_id = models.PositiveIntegerField(verbose_name='Telegram ID кампании')
    refer_url = models.URLField(verbose_name='Ссылка на кампанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Рекламная кампания'
        verbose_name_plural = 'Рекламные кампании'


class User(models.Model):
    telegram_id = models.PositiveBigIntegerField(verbose_name='Telegram ID')
    first_name = models.CharField(max_length=40, verbose_name='Имя', null=True)
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)

    class Meta:
        abstract = True


class Client(User):
    personal_data_consent = models.BooleanField(verbose_name='Согласие на обработку персональных данных', default=False)
    advertisement = models.ForeignKey(Advertisement,
                                      on_delete=models.PROTECT,
                                      verbose_name='Рекламная кампания',
                                      null=True,
                                      blank=True,
                                      related_name='clients',
                                      )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.telegram_id}: {self.first_name}'


class Staff(User):
    STAFF_ROLE_CHOICES = (
        ('admin', 'Админ'),
        ('florist', 'Флорист'),
        ('currier', 'Курьер'),
    )
    last_name = models.CharField(max_length=40, verbose_name='Фамилия')
    role = models.CharField(max_length=40, verbose_name='Роль', choices=STAFF_ROLE_CHOICES)
    start_date = models.DateTimeField(verbose_name='Дата начала работы', auto_now_add=True)
    end_date = models.DateTimeField(verbose_name='Дата увольнения', null=True, blank=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.telegram_id}: {self.first_name} {self.last_name} - {self.role}'


class Occasion(models.Model):
    name = models.CharField(max_length=40, verbose_name='Повод')

    class Meta:
        verbose_name = 'Повод'
        verbose_name_plural = 'Поводы'

    def __str__(self):
        return self.name


class Colors(models.Model):
    name = models.CharField(max_length=40, verbose_name='Цвет')

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'

    def __str__(self):
        return self.name


class Gamma(models.Model):
    name = models.CharField(max_length=40, verbose_name='Гамма')

    class Meta:
        verbose_name = 'Гамма'
        verbose_name_plural = 'Гаммы'

    def __str__(self):
        return self.name


class Genus(models.Model):
    name = models.CharField(max_length=40, verbose_name='Род растения')

    class Meta:
        verbose_name = 'Род растения'
        verbose_name_plural = 'Роды растений'

    def __str__(self):
        return self.name


class Flower(models.Model):
    genus = models.ForeignKey(Genus, on_delete=models.PROTECT, verbose_name='Род растения')
    name = models.CharField(max_length=40, verbose_name='Название цветка')
    length = models.PositiveIntegerField(verbose_name='Длина цветка', help_text='в сантиметрах', null=True, blank=True)
    color = models.ForeignKey(Colors,
                              on_delete=models.PROTECT,
                              verbose_name='Цвет',
                              related_name='flowers',
                              )

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'

    def __str__(self):
        if self.length is None:
            return f'{self.name}, цвет: {self.color}'
        return f'{self.name} ({self.length} см.), цвет: {self.color}'


class Greenery(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название зелени')

    class Meta:
        verbose_name = 'Зелень'
        verbose_name_plural = 'Зелень'

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    image = models.ImageField(verbose_name='Изображение', upload_to='bouquets')
    name = models.CharField(max_length=40, verbose_name='Название букета')
    flowers = models.ManyToManyField(Flower,
                                     through='FlowerComposition',
                                     verbose_name='Цветы',
                                     related_name='bouquets',
                                     )
    greenery = models.ManyToManyField(Greenery,
                                      through='GreeneryComposition',
                                      verbose_name='Зелень',
                                      related_name='bouquets',
                                      )
    meaning = models.TextField(verbose_name='Значение')
    wrapping = models.CharField(max_length=40, verbose_name='Упаковка', null=True, blank=True)
    occasion = models.ManyToManyField(Occasion,
                                      verbose_name='Повод',
                                      related_name='bouquets',
                                      )
    price = models.PositiveIntegerField(verbose_name='Цена')

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    def __str__(self):
        return self.name


class FlowerComposition(models.Model):
    bouquet = models.ForeignKey(Bouquet,
                                on_delete=models.PROTECT,
                                verbose_name='Букет',
                                related_name='flower_composition',
                                )
    flower = models.ForeignKey(Flower,
                               on_delete=models.PROTECT,
                               verbose_name='Цветок',
                               related_name='flower_composition',
                               )
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Цветы в букетах'
        verbose_name_plural = 'Цветы в букетах'

    def __str__(self):
        return f'{self.bouquet.name}: {self.flower.name} - {self.quantity} шт.'


class GreeneryComposition(models.Model):
    bouquet = models.ForeignKey(Bouquet,
                                on_delete=models.PROTECT,
                                verbose_name='Букет',
                                related_name='greenery_composition',
                                )
    greenery = models.ForeignKey(Greenery,
                                 on_delete=models.PROTECT,
                                 verbose_name='Зелень',
                                 related_name='greenery_composition',
                                 )
    quantity = models.FloatField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Зелень в букетах'
        verbose_name_plural = 'Зелень в букетах'

    def __str__(self):
        return f'{self.bouquet.name}: {self.greenery.name} - {self.quantity} шт.'


class ConsultingStatus(models.Model):
    name = models.CharField(max_length=40, verbose_name='Статус')

    class Meta:
        verbose_name = 'Статус консультации'
        verbose_name_plural = 'Статусы консультаций'

    def __str__(self):
        return self.name


class Consulting(models.Model):
    client = models.ForeignKey(Client,
                               on_delete=models.PROTECT,
                               verbose_name='Клиент',
                               related_name='consultings',
                               )
    florist = models.ForeignKey(Staff,
                                on_delete=models.PROTECT,
                                verbose_name='Флорист',
                                limit_choices_to={'role': 'florist'},
                                related_name='consultings',
                                )
    status = models.ManyToManyField(ConsultingStatus,
                                    through='ConsultingStatusHistory',
                                    )
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата изменения', auto_now=True)
    contact_phone = models.CharField(max_length=40, verbose_name='Контактный телефон')
    first_call_at = models.DateTimeField(verbose_name='Дата и время звонка', null=True, blank=True)
    occasion = models.ForeignKey(Occasion,
                                 on_delete=models.PROTECT,
                                 verbose_name='Повод',
                                 related_name='consultings',
                                 )
    occasion_text = models.CharField(max_length=40, verbose_name='Повод (уточнение)', blank=True)
    gamma = models.ForeignKey(Gamma,
                              on_delete=models.PROTECT,
                              verbose_name='Гамма',
                              related_name='consultings',
                              )

    class Meta:
        verbose_name = 'Консультация'
        verbose_name_plural = 'Консультации'

    def __str__(self):
        return f'{self.client}: {self.florist}'


class ConsultingStatusHistory(models.Model):
    consulting = models.ForeignKey(Consulting,
                                   on_delete=models.PROTECT,
                                   verbose_name='Консультация',
                                   related_name='status_history',
                                   )
    status = models.ForeignKey(ConsultingStatus,
                               on_delete=models.PROTECT,
                               verbose_name='Статус',
                               related_name='status_history',
                               )
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'История статусов консультации'
        verbose_name_plural = 'Истории статусов консультаций'

    def __str__(self):
        return f'{self.consulting}: {self.status}'


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'В работе'),
        ('ready', 'Готов'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    client = models.ForeignKey(Client,
                               on_delete=models.PROTECT,
                               verbose_name='Клиент',
                               related_name='orders',
                               )
    bouquet = models.ForeignKey(Bouquet,
                                on_delete=models.PROTECT,
                                verbose_name='Букет',
                                related_name='orders',
                                )
    consultation = models.ForeignKey(Consulting,
                                     on_delete=models.PROTECT,
                                     verbose_name='Консультация',
                                     related_name='orders',
                                     null=True,
                                     blank=True,
                                     )
    status = models.CharField(max_length=40, verbose_name='Статус', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата изменения', auto_now=True)
    delivery_date = models.DateTimeField(verbose_name='Дата доставки')
    delivery_address = models.CharField(max_length=200, verbose_name='Адрес доставки')
    contact_phone = models.CharField(max_length=20, verbose_name='Контактный телефон')
    contact_name = models.CharField(max_length=40, verbose_name='Контактное лицо')
    currier = models.ForeignKey(Staff,
                                on_delete=models.PROTECT,
                                verbose_name='Курьер',
                                limit_choices_to={'role': 'currier'},
                                related_name='orders',
                                null=True,
                                blank=True,
                                )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.bouquet.name}: ' \
               f'{self.delivery_date} по адресу: {self.delivery_address} - {self.status}'
