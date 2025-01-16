from django.db import models
from rest_framework.exceptions import ValidationError

from category.models import CostType, Category
from core import utils
from user.models import Store, Agent, Driver, ModelAdmin


class Cost(models.Model):
    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    cost = models.FloatField('Расход', default=0)
    costType = models.ForeignKey(CostType, models.SET_NULL, null=True, blank=True, verbose_name='Тип продажи')
    bonusAmount = models.FloatField('Бонус', default=0)

    def __str__(self):
        return str(self.cost)


class NoStripCharField(models.CharField):
    def to_python(self, value):
        if value is None:
            return value
        return str(value)


class PreserveWhitespaceCharField(models.CharField):
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        return value  # Return the value as is, without stripping whitespace


def no_trim_validator(value):
    if value != value.rstrip():
        raise ValidationError('Пробелы в конце строки недопустимы.')


class Item(models.Model):
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    name = models.CharField('Название', max_length=200)
    photo = models.TextField('Фото товара', blank=True)
    costIn = models.FloatField('Внутренние расходы', default=0)
    costs = models.ManyToManyField(Cost, blank=True, verbose_name='Costs')
    category = models.ForeignKey(Category, models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    quantity = models.IntegerField('Количество', default=0)
    code = models.CharField('Наименование код', max_length=250, blank=True)
    # oneC_code = PreserveWhitespaceCharField(max_length=250, blank=True)
    author = models.CharField('Автор', max_length=250, blank=True)
    weight = models.FloatField('Вес', default=0)
    isSale = models.BooleanField('Is sale?', default=False)
    saleCost = models.FloatField('Цена расспродажи', default=0)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.code = self.code
        super(Item, self).save(*args, **kwargs)


class CostChangeHistory(models.Model):
    class Meta:
        verbose_name = 'История изменений продаж'
        verbose_name_plural = 'Истории изменений продаж'

    item = models.ForeignKey(Item, models.SET_NULL, null=True, blank=True, verbose_name='Товар')
    dateChanged = models.DateTimeField('Дата измнения', auto_now_add=True)
    costs = models.ManyToManyField(Cost, blank=True, verbose_name='Costs')

    def __str__(self):
        return str(self.item.name)


class OrderItem(models.Model):
    class Meta:
        verbose_name = 'Заказной товар'
        verbose_name_plural = 'Заказные товары'

    item = models.ForeignKey(Item, models.SET_NULL, null=True, blank=True, verbose_name='Товар')
    count = models.FloatField('Count', default=0)
    soldCost = models.FloatField('Стоимость продажи', default=0)
    costType = models.ForeignKey(CostType, models.SET_NULL, null=True, blank=True, verbose_name='Тип продажи')

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    dateCreated = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформления заказа')
    store = models.ForeignKey(Store, models.SET_NULL, null=True, blank=True, verbose_name='Магазин')
    agent = models.ForeignKey(Agent, models.SET_NULL, null=True, blank=True, verbose_name='Агент')
    driver = models.ForeignKey(Driver, models.SET_NULL, null=True, blank=True, verbose_name='Водитель')
    costType = models.ForeignKey(CostType, models.SET_NULL, null=True, blank=True, verbose_name='Тип продажи')
    items = models.ManyToManyField(OrderItem, blank=True, verbose_name='Товары')
    totalCost = models.FloatField('Общая сумма', default=0)
    status = models.CharField('Статус', max_length=20, choices=utils.ORDER_TYPE, default=utils.NEW)
    comment = models.TextField('Комментарий', blank=True)
    dateDelivered = models.DateTimeField('Дата доставки', null=True, blank=True)
    lat = models.FloatField('LAT', default=0)
    lon = models.FloatField('LON', default=0)
    signature = models.CharField('Подпись', max_length=250, blank=True)
    photo = models.TextField('Фото', blank=True)
    delComment = models.TextField('Комментарий доставщика', blank=True)
    is_sync_oneC = models.BooleanField('Статус синхронизации', default=False)
    paymentStatus = models.CharField('Статус оплаты', choices=utils.PAYMENT_STATUS, default=utils.NOT_PAID,
                                     max_length=20)
    amountLeft = models.FloatField('Остаток суммы', default=0)
    weight = models.FloatField('Вес', default=0)
    shipping_date = models.DateField('Дата отгрузки', blank=True, null=True)

    def __str__(self):
        return str(self.dateCreated)


class Transaction(models.Model):
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    description = models.TextField('Описание', blank=True)
    amount = models.FloatField('Количество', default=0)
    dateCreated = models.DateTimeField('Дата создания', auto_now_add=True)
    agent = models.ForeignKey(Agent, models.SET_NULL, null=True, blank=True, verbose_name='Агент')

    def __str__(self):
        return str(self.dateCreated)


class Shablon(models.Model):
    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны'

    agent = models.ForeignKey(Agent, models.CASCADE, verbose_name='Агент')
    monStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины в понедельник',
                                       related_name='monStores')
    monDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель в понедельник',
                                  related_name='monDriver')
    tueStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины во вторник',
                                       related_name='tueStores')
    tueDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель во вторник',
                                  related_name='tueDriver')
    wedStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины в среду',
                                       related_name='wedStores')
    wedDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель в среду',
                                  related_name='wedDriver')
    thuStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины в четверг',
                                       related_name='thuStores')
    thuDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель в четверг',
                                  related_name='thuDriver')
    friStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины в пятницу',
                                       related_name='friStores')
    friDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель в пятницу',
                                  related_name='friDriver')
    satStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины в субботу',
                                       related_name='satStores')
    satDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель в субботу',
                                  related_name='satDriver')
    sunStores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины в воскресенье',
                                       related_name='sunStores')
    sunDriver = models.ForeignKey(Driver, models.SET_NULL, null=True, verbose_name='Водитель в воскресенье',
                                  related_name='sunDriver')

    def __str__(self):
        return str(self.agent.name)


class TransactionOrder(models.Model):
    class Meta:
        verbose_name = 'Транзакция заказов'
        verbose_name_plural = 'Транзакции заказов'

    sum = models.FloatField('Сумма')
    comment = models.TextField('Комментарий', blank=True)
    order = models.ForeignKey(Order, models.CASCADE, verbose_name='Заказ')
    dateCreated = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return str(self.dateCreated)


class OrderHistory(models.Model):
    class Meta:
        verbose_name = 'История изменения заказов'
        verbose_name_plural = 'Истории изменений заказов'

    order = models.ForeignKey(Order, models.CASCADE, verbose_name='Заказ')
    description = models.TextField('Описание', blank=True)
    addedItems = models.ManyToManyField(OrderItem, blank=True, verbose_name='Добавленные товары', related_name='addedItems')
    removeItems = models.ManyToManyField(OrderItem, blank=True, verbose_name='Удаленные товары', related_name='removeItems')
    admin = models.ForeignKey(ModelAdmin, models.SET_NULL, null=True, blank=True, verbose_name='Администратор')
    dateCreated = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время изменения')

    def __str__(self):
        return str(self.dateCreated)


class ReturnsOrder(models.Model):
    class Meta:
        verbose_name = 'Возврат'
        verbose_name_plural = 'Возвраты'

    order = models.ForeignKey(Order, models.SET_NULL, null=True, blank=True, verbose_name='Заказ')
    # returnedItems = models.ManyToManyField(ReturnsItem, blank=True, verbose_name='Товары')
    comment = models.TextField('Комментарий', blank=True)

    @property
    def returnedItems(self):
        return self.returnsitem_set.all()

    def __str__(self):
        return str(self.id)


class ReturnsItem(models.Model):
    item = models.ForeignKey(Item, models.SET_NULL, null=True, blank=True, verbose_name='Товар')
    quantity = models.FloatField('Количество', default=0)
    soldCost = models.FloatField('Sold cost', default=0)
    returnedOrder = models.ForeignKey(ReturnsOrder, models.SET_NULL, null=True, blank=True, verbose_name='Возврат')

    def __str__(self):
        return str(self.id)
