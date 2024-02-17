from django.contrib import admin
import requests
from app.models import Advertising
from environs import Env

env = Env()
env.read_env()

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

