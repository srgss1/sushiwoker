from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ('name', 'price', 'is_active')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "-"
    preview_image.short_description = "Превью"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active', 'product_count')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'order', 'is_active')
        }),
        ('Контент', {
            'fields': ('image', 'description'),
        }),
    )

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Кол-во продуктов"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview_image', 'category', 'price', 'is_popular', 'is_new', 'is_active')
    list_filter = ('category', 'is_popular', 'is_new', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_popular', 'is_new', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('preview_image',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Изображение', {
            'fields': ('image', 'preview_image'),
        }),
        ('Цена и вес', {
            'fields': ('price', 'weight'),
        }),
        ('Флаги', {
            'fields': ('is_popular', 'is_new', 'is_active'),
        }),
    )

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="100" />', obj.image.url)
        return "-"
    preview_image.short_description = "Текущее изображение"