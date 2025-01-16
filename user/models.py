from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

from category.models import CostType, Region
from user import utils


class UserManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, login, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not login:
            raise ValueError('User must have an Email or Phone')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password):
        """create a superuser"""
        user = self.create_user(login, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def clean(self):
        self.set_password(self.password)


class User(AbstractBaseUser, PermissionsMixin):
    """Model for user"""
    name = models.CharField(max_length=200, verbose_name="ФИО")
    birthdate = models.DateField(verbose_name='День рождения', null=True, blank=True)
    address = models.CharField("Адрес", max_length=200, null=True, blank=True)
    phoneNumber = models.CharField("Номер телефона", max_length=200, null=True, blank=True)
    photo = models.TextField('Аватар', null=True, blank=True)
    user_type = models.CharField("Тип пользователя", max_length=50, choices=utils.USER_TYPE, default=utils.ADMINISTRATOR)
    login = models.CharField(max_length=200, unique=True, verbose_name="Логин")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    reset_code = models.CharField(verbose_name='Код для сброса пароля', max_length=6, blank=True)
    passport_front = models.TextField('Паспорт фронтальная сторона', null=True, blank=True)
    passport_back = models.TextField('Паспорт обратная сторона')
    balance = models.FloatField('Баланс', default=0,)
    oneC_code = models.CharField('1С Код', max_length=250, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'login'


class ModelAdmin(User):
    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    fullname = models.CharField('ФИО', max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(ModelAdmin, self).save(*args, **kwargs)
        self.user_type = utils.ADMINISTRATOR

    def clean(self):
        self.user_type = utils.ADMINISTRATOR


class Manager(User):
    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

    fullname = models.CharField('ФИО', max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(Manager, self).save(*args, **kwargs)
        self.user_type = utils.MANAGER

    def clean(self):
        self.user_type = utils.MANAGER


class Agent(User):
    class Meta:
        verbose_name = 'Агент'
        verbose_name_plural = 'Агенты'

    costTypes = models.ManyToManyField(CostType, blank=True, verbose_name='Типы продаж')

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(Agent, self).save(*args, **kwargs)
        self.user_type = utils.AGENT

    def clean(self):
        self.user_type = utils.AGENT


class Store(User):
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    contactName = models.CharField('Контактное имя', max_length=200)
    phoneNumber1 = models.CharField('Контактный номер 1', max_length=200, blank=True)
    phoneNumber2 = models.CharField('Контактный номер 2', max_length=200, blank=True)
    phoneNumber3 = models.CharField('Контактный номер 3', max_length=200, blank=True)
    score = models.FloatField('Cчет', default=0)
    lat = models.FloatField('LAT', default=0)
    lon = models.FloatField('LON', default=0)
    costType = models.ForeignKey(CostType, models.SET_NULL, null=True, blank=True)
    dateCreated = models.DateTimeField('Дата создания', auto_now_add=True)
    area = models.FloatField('Площадь', default=0)
    # docs = ArrayField(models.TextField(), verbose_name='Документ', blank=True)
    documents = ArrayField(models.TextField(), blank=True, null=True, verbose_name='Документы')
    store_agent = models.ForeignKey(Agent, models.SET_NULL, null=True, blank=True, verbose_name='Агент')
    region = models.ForeignKey(Region, models.SET_NULL, null=True, blank=True, verbose_name='Район')
    guid = models.CharField('GUID', max_length=250, blank=True)

    def __str__(self):
        return str(self.name)

    def clean(self):
        self.user_type = utils.STORE

    def save(self, *args, **kwargs):
        super(Store, self).save(*args, **kwargs)
        self.user_type = utils.STORE


class Driver(User):
    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    contactName = models.CharField('Контактное имя', max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(Driver, self).save(*args, **kwargs)
        self.user_type = utils.DRIVER

    def clean(self):
        self.user_type = utils.DRIVER


class PlanStore(models.Model):
    class Meta:
        verbose_name = 'План магазин'
        verbose_name_plural = 'Планы магазина'

    store = models.ForeignKey(Store, models.CASCADE, verbose_name='Магазин')
    status = models.CharField('Статус', max_length=20, choices=utils.STORE_STATUS, default=utils.NEW)
    photo = models.TextField('Ccылка на фото', blank=True)
    comment = models.TextField('Комментарий', blank=True)
    madeOrder = models.BooleanField('Заказано', default=False)

    def __str__(self):
        return str(self.id) + " " + str(self.store)


class DayPlan(models.Model):
    class Meta:
        verbose_name = 'Дневной план'
        verbose_name_plural = 'Дневные планы'

    day = models.CharField('День недели', max_length=50, choices=utils.DAYS_OF_WEEK, default=utils.MONDAY)
    agent = models.ForeignKey(Agent, models.CASCADE, verbose_name='Агент')
    status = models.CharField('Статус', max_length=20, choices=utils.STATUS, default=utils.NEW)
    # stores = models.ManyToManyField(Store, blank=True, verbose_name='Магазины')
    stores_plan = models.ManyToManyField(PlanStore, blank=True, verbose_name='Планы Магазин')
    driver = models.ForeignKey(Driver, models.SET_NULL, null=True, blank=True, verbose_name='Водитель')
    dateCreated = models.DateTimeField('Дата создания', default=timezone.now)
    dateVisit = models.DateField('Дата посещения', blank=True, null=True)

    def __str__(self):
        return str(self.day) + " " + str(self.status)


class UsersLog(models.Model):
    class Meta:
        verbose_name = 'Логи пользователей'
        verbose_name_plural = 'Логи пользователей'

    user_name = models.CharField('Пользователь', max_length=250)
    user_id = models.CharField('ID пользователя', max_length=100)
    request_body = models.TextField('Request body')
    bElim_response_body = models.TextField('Бай элим response', blank=True)
    # organic_request_body = models.TextField('Органик request body')
    organic_response_body = models.TextField('Органик response', blank=True)
    dateCreated = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return str(self.user_name)
