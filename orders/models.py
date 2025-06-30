from django.conf import settings
from django.db import models

from core.models import Product


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('preparing', 'Готовится'),
        ('delivering', 'В пути'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    )

    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='order')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # Контактные данные
    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    # Адрес доставки
    address = models.TextField()
    entrance = models.CharField(max_length=10, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    apartment = models.CharField(max_length=10, blank=True)
    comment = models.TextField(blank=True)

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Статус и оплата
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    is_paid = models.BooleanField(default=False)

    # Стоимость
    delivery_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Заказ #{self.id} - {self.get_status_display()}"
