from django.urls import path
from app import views

urlpatterns = [
    path('',views.index,name="index"),
    path('contact',views.contact,name="contact"),
    path('product/<id>',views.product,name="product"),
    path('about',views.about,name="about"),
    path('team',views.team,name="about"),
    path('checkout/', views.checkout, name="Checkout"),
    path('handlerequest/', views.handlerequest, name="HandleRequest"),
    path("callback/", views.callback, name="callback"),
    path("products/<name>", views.list, name="products"),
    path("orders", views.myorders, name="products")
]
