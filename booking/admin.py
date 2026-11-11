from django.contrib import admin

from .models import Booking, BookingItem


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'start_date', 'end_date', 'status']
    list_filter = ['status']
    inlines = [BookingItemInline]

# Register your models here.
