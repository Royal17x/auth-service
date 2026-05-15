from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('products/', views.ProductsView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('orders/', views.OrdersView.as_view(), name='orders'),
    path('shops/', views.ShopsView.as_view(), name='shops'),
    path('my-permissions/', views.MyPermissionsView.as_view(), name='my-permissions'),
]