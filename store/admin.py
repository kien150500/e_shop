from django.contrib import admin
from .models import Category, Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'full_name', 'email', 'created', 'paid')
    list_filter = ('paid', 'created')


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
