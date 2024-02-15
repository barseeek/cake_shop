from django.contrib import admin

from .models import (Client, BaseCake, CustomCake, Order, OrderBaseCake,
                     Advertising)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(BaseCake)
class BaseCakeAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomCake)
class CustomCakeAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderBaseCake)
class OrderBaseCakeAdmin(admin.ModelAdmin):
    pass


@admin.register(Advertising)
class AdvertisingAdmin(admin.ModelAdmin):
    pass
