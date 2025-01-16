from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets, status, permissions, generics, authentication
import openpyxl
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from category import models, serializers


class CostTypeViewSet(viewsets.ModelViewSet):
    queryset = models.CostType.objects.all()
    serializer_class = serializers.CostTypeSerializer
    pagination_class = None


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    pagination_class = None


class AksiyaViewSet(viewsets.ModelViewSet):
    queryset = models.Aksiya.objects.all()
    serializer_class = serializers.AksiyaSerializer
    pagination_class = None


class StoriesViewSet(viewsets.ModelViewSet):
    queryset = models.Stories.objects.all()
    serializer_class = serializers.StoriesSerializer
    pagination_class = None

    def get_queryset(self):
        return self.queryset.order_by('-date')


class FileViewSet(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = models.ModelImage.objects.all()
    serializer_class = serializers.ImageSerializer


class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer


class FAQViewSet(viewsets.ModelViewSet):
    queryset = models.FAQ.objects.all()
    serializer_class = serializers.FAQSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('priority', )
