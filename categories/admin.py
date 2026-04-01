from django.contrib import admin
from .models import WFM, MFM, KFM, WFMSizeAvailability, MFMSizeAvailability, KFMSizeAvailability, Purchase

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

admin.site.register(Purchase)