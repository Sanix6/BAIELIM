from django.db import models

from category import imggenerate


class CostType(models.Model):
    class Meta:
        verbose_name = 'Тип продажи'
        verbose_name_plural = 'Типы продаж'

    name = models.CharField('Название', max_length=200)
    # test = models.TextField('Тестовый', null=True, blank=True)
    one_guid = models.TextField('guid', null=True, blank=True)
    guid_organic = models.TextField('guid_organic', blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = 'Категория',
        verbose_name_plural = 'Категории'

    name = models.CharField('Название', max_length=200)
    nameKg = models.CharField('Аталышы', max_length=200, null=True, blank=True)
    nameEn = models.CharField('Name', max_length=200, null=True, blank=True)
    icon = models.TextField('Иконка', null=True, blank=True)
    test = models.TextField('Тестовый', null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Aksiya(models.Model):
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акция'

    photo = models.TextField('Фото', blank=True, null=True)
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание', blank=True)
    deadline = models.DateField('Срок окончания', null=True, blank=True)

    def __str__(self):
        return str(self.title)


class Stories(models.Model):
    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'Истории'

    photo = models.TextField('Фото')
    date = models.DateField('Дата', null=True, blank=True)

    def __str__(self):
        return str(self.date)


class File(models.Model):
    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

    title = models.CharField('Заголовок', max_length=200)
    file = models.FileField('Файл', upload_to=imggenerate.all_file_path)

    def __str__(self):
        return str(self.title)


class ModelImage(models.Model):
    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'

    title = models.CharField('Заголовок', max_length=200)
    image = models.ImageField('Фото', upload_to=imggenerate.all_image_path)

    def __str__(self):
        return str(self.title)


class Region(models.Model):
    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Район'

    name = models.CharField('Название', max_length=250)

    def __str__(self):
        return str(self.name)


class FAQ(models.Model):
    class Meta:
        verbose_name = 'Часто задаваемые вопросы'
        verbose_name_plural = 'Часто задаваемые вопросы'

    question = models.TextField('Вопрос')
    answer = models.TextField('Ответ')
    priority = models.FloatField('Приоритет', default=0)

    def __str__(self):
        return str(self.question)
