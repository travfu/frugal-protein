from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:pk>/', views.ProductView.as_view(), name='product'),
]