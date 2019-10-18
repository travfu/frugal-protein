from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('product/<int:pk>/', views.ProductView.as_view(), name='product'),
]