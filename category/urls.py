from django.urls import path, include
from . import views
from .views import *
from rest_framework.routers import SimpleRouter

app_name = 'category'

router = SimpleRouter()

router.register(r'costType', views.CostTypeViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'aksiya', views.AksiyaViewSet)
router.register(r'stories', views.StoriesViewSet)
router.register(r'files', views.FileViewSet)
router.register(r'image', views.ImageViewSet)
router.register(r'region', views.RegionViewSet)
router.register(r'FAQ', views.FAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
