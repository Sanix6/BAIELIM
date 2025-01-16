from rest_framework import serializers
from category import models
from django.contrib.auth import get_user_model, authenticate, password_validation
from django_filters import rest_framework as filters
User = get_user_model()
from rest_framework.authtoken.models import Token


class CostTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CostType
        # fields = ('name', )
        fields = ('id', 'name', 'one_guid', 'guid_organic')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class AksiyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Aksiya
        fields = '__all__'


class StoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stories
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = ('id', 'title', 'file')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelImage
        fields = ('id', 'title', 'image')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ('id', 'name')


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FAQ
        fields = ('id', 'question', 'answer', 'priority')
