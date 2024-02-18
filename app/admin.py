from django.contrib import admin
import requests
from environs import Env

from .models import (Client, BaseCake, CustomCake, Order, OrderBaseCake,
                     Advertising)

env = Env()
env.read_env()


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
class AdvertisingModel(admin.ModelAdmin):
    list_display = ('url', 'text', 'responses',)
    readonly_fields = ('url','responses',)


    def changelist_view(self, request, extra_context=None):
        # Ваша логика обновления модели
        advertising = Advertising.objects.all()
        headers = {
            "Authorization": f"Bearer {env.str('TLY_API_TOKEN')}"
        }
        url = "https://t.ly/api/v1/link/stats"
        for ad in advertising:
            params = {"short_url": ad.url}
            response = requests.get(url,
                                    headers=headers,
                                    params=params)
            response.raise_for_status()
            ad.responses = response.json()["clicks"]
        Advertising.objects.bulk_update(advertising, ['responses'])
        return super().changelist_view(request, extra_context=extra_context)

