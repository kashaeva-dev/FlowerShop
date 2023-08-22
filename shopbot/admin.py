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


admin.site.register(Advertisement)
admin.site.register(Client)
admin.site.register(Staff)
admin.site.register(Colors)
admin.site.register(Gamma)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(Occasion)
admin.site.register(Flower)
admin.site.register(Greenery)
admin.site.register(FlowerComposition)
admin.site.register(GreeneryComposition)
admin.site.register(Genus)
