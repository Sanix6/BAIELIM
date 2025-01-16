from django.urls import path, include
from . import views
from .views import *
from rest_framework.routers import SimpleRouter

app_name = 'core'

router = SimpleRouter()

router.register(r'cost', views.CostViewSet)
router.register(r'item', views.ItemViewSet)
router.register(r'costChangeHistory', views.CostChangeHistoryViewSet)
router.register(r'orderItem', views.OrderItemViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'transaction', views.TransactionViewSet)
router.register(r'shablon', views.ShablonViewSet)
router.register(r'transactionOrder', views.TransactionOrderViewSet)
router.register(r'orderHistory', views.OrderHistoryViewSet)
router.register(r'order_second', views.OrderViewSetSecond)
router.register(r'return_order', views.ReturnOrderViewSet)
router.register(r'return_item', views.ReturnItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('import_items/', views.ImportItemsView.as_view()),
    path('create_plan/', views.CreatePlanView.as_view()),
    path('import_items/', views.ImportItemsView.as_view()),
    path('synchronize_items/', views.SynchronizeItemsView.as_view()),
    path('synchronize_agents/', views.SynchronizeAgentsView.as_view()),
    path('synchronize_drivers/', views.SynchronizeDriversView.as_view()),
    # path('synchronize_stores/', views.SynchronizeStoresView.as_view()),
    path('synchronize_orders/', views.SynchronizeOrdersView.as_view()),
    path('count_orders/', views.CountOrdersView.as_view()),
    path('orders_statistic/', views.OrdersStatisticView.as_view()),
    path('get_all_items/', views.GetAllItemsView.as_view()),
    path('count_items/', views.ItemCountView.as_view()),
    path('totalCount_of_orders/', views.TotalCountOfOrdersView.as_view()),
    path('marginality/', views.MarginalityView.as_view()),
    path('synchronize_costs/', views.SynchronizeCostView.as_view()),
    path('drivers_items/', views.DriversItemsView.as_view()),
    path('list_of_stores_selling/', views.ListOfStoresSellingView.as_view()),
    path('drivers_stores/', views.DriversStoresView.as_view()),
    path('stores_orders/', views.OrdersByDateAndCostAPIView.as_view())
]
