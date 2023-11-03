from django.contrib import admin
from Auction.models import Users, Payments, Items, Bids, Category

# Register your models here.
admin.site.register(Users)
admin.site.register(Payments)
admin.site.register(Items)
admin.site.register(Bids)
admin.site.register(Category)