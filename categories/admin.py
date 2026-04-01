from django.contrib import admin

from .models import (
    BagItem,
    KFM,
    KFMSizeAvailability,
    MFM,
    MFMSizeAvailability,
    Order,
    OrderLine,
    Purchase,
    WFM,
    WFMSizeAvailability,
)


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    readonly_fields = ('product_label', 'line_total')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('order_number', 'user__username', 'phone')
    inlines = [OrderLineInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')

class SizeAvailabilityInline(admin.TabularInline):
    extra = 1
    max_num = 5

class WFMSizeAvailabilityInline(SizeAvailabilityInline):
    model = WFMSizeAvailability
    verbose_name = "Size"
    verbose_name_plural = "Sizes"

class MFMSizeAvailabilityInline(SizeAvailabilityInline):
    model = MFMSizeAvailability
    verbose_name = "Size"
    verbose_name_plural = "Sizes"

class KFMSizeAvailabilityInline(SizeAvailabilityInline):
    model = KFMSizeAvailability
    verbose_name = "Size"
    verbose_name_plural = "Sizes"

@admin.register(WFM)
class WFMAdmin(admin.ModelAdmin):
    inlines = [WFMSizeAvailabilityInline]
    list_display = ['company', 'model', 'price', 'display_available_sizes']

    def display_available_sizes(self, obj):
        sizes = obj.sizes.filter(quantity__gt=0).values_list('size', flat=True)
        return ', '.join(sizes) if sizes else 'No sizes available'
    display_available_sizes.short_description = 'Available Sizes'

@admin.register(MFM)
class MFMAdmin(admin.ModelAdmin):
    inlines = [MFMSizeAvailabilityInline]
    list_display = ['company', 'model', 'price', 'display_available_sizes']

    def display_available_sizes(self, obj):
        sizes = obj.sizes.filter(quantity__gt=0).values_list('size', flat=True)
        return ', '.join(sizes) if sizes else 'No sizes available'
    display_available_sizes.short_description = 'Available Sizes'

@admin.register(KFM)
class KFMAdmin(admin.ModelAdmin):
    inlines = [KFMSizeAvailabilityInline]
    list_display = ['company', 'model', 'price', 'display_available_sizes']

    def display_available_sizes(self, obj):
        sizes = obj.sizes.filter(quantity__gt=0).values_list('size', flat=True)
        return ', '.join(sizes) if sizes else 'No sizes available'
    display_available_sizes.short_description = 'Available Sizes'

@admin.register(BagItem)
class BagItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'product_id', 'size', 'quantity')


admin.site.register(Purchase)