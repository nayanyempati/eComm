
from app import views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', views.index),
    path('product/<id>', views.product, name="product"),
    path('about', views.about, name="about"),
    path('team', views.team, name="about"),
    path('checkout/', views.checkout, name="Checkout"),
    path("callback/", views.callback, name="callback"),
    path("products/<name>", views.Productlist, name="products"),
]
