from django.contrib import admin
from .models import Customer, Product, Tracker, Reminder
# Register your models here.

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Tracker)
admin.site.register(Reminder)
