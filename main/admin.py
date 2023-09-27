from django.contrib import admin
from .models import (
    Address,
    Genre,
    Like,
    Notification,
    Order,
    Payment,
    Product,
    ProductImage,
)

# Register your models here.
admin.site.register(Address)
admin.site.register(Genre)
admin.site.register(Like)
admin.site.register(Notification)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Product)
admin.site.register(ProductImage)