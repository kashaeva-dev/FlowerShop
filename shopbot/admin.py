from django.contrib import admin

from shopbot.models import (
    Advertisement,
    Client,
    Staff,
    Colors,
    Gamma,
    Bouquet,
    Order,
    Occasion,
    Flower,
    Greenery,
    FlowerComposition,
    GreeneryComposition,
    Genus,
)


class FlowerCompositionInline(admin.TabularInline):
    model = FlowerComposition
    extra = 1


class GreeneryCompositionInline(admin.TabularInline):
    model = GreeneryComposition
    extra = 1


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    inlines = (FlowerCompositionInline,
               GreeneryCompositionInline,
               )


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_filter = ('genus',)


admin.site.register(Advertisement)
admin.site.register(Client)
admin.site.register(Staff)
admin.site.register(Colors)
admin.site.register(Gamma)
admin.site.register(Order)
admin.site.register(Occasion)
admin.site.register(Greenery)
admin.site.register(Genus)
