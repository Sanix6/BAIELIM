from django.urls import path, include
from . import views
from .views import *
from rest_framework.routers import SimpleRouter

app_name = 'user'

router = SimpleRouter()

router.register(r'administrator', views.AdministratorViewSet)
router.register(r'manager', views.ManagerViewSet)
router.register(r'agent', views.AgentViewSet)
router.register(r'store', views.StoreViewSet)
router.register(r'driver', views.DriverViewSet)

router.register(r'dayPlan', views.DayPlanViewSet)
router.register(r'storePlan', views.StorePlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get_stores/', views.GetStoresView.as_view()),
    path('new_day_plans/', views.NewDayPlanView.as_view()),
    path('get_stores_until_june/', views.GetStoreUntilJuneView.as_view()),
    # path('get_stores_by_hundred/', views.GetJulyStoresView.as_view()),
    path('get_stores_for_oneC/', views.GetStoreForOneCView.as_view()),
    path('change-password/without-old_password/', views.ChangePasswordWithoutOldPasswordView.as_view(),
         name='change_password_without_old_password'),
    path('synchronize_stores/', views.SynchronizeStoresView.as_view()),
    path('epta/', views.EptaView.as_view()),
    path('store_code_update/', views.UpdateStoreOneCCodeView.as_view()),
    path('export/stores/', export_to_excel, name='export_stores'),
]
