from django.contrib import admin

from app.models import Orders, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(Orders)
