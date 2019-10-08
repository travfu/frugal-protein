from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='search'),
    path('product/<int:pk>/', views.ProductView.as_view(), name='product'),
]