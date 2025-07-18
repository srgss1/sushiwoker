import logging

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models import Product


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    @property
    def total_price(self):
        """Общая стоимость товаров в корзине"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username}"
        return f"Корзина (анонимная) #{self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ('cart', 'product')

    @property
    def total_price(self):
        """Стоимость позиции (цена * количество)"""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} в корзине #{self.cart.id}"

    def save(self, *args, **kwargs):
        # Логируем сохранение
        from django.db import connection
        queries_before = len(connection.queries)

        super().save(*args, **kwargs)

        queries_after = len(connection.queries)
        logger = logging.getLogger(__name__)
        logger.info(f"Сохранение CartItem: id={self.id}, product={self.product_id}, "
                    f"quantity={self.quantity}, queries={queries_after - queries_before}")

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
    phone = models.CharField("Телефон", max_length=20)
    name = models.CharField("Имя", max_length=100)
    email = models.EmailField("Email", blank=True)

    # Адрес доставки
    address = models.TextField("Адрес")
    entrance = models.CharField("Подъезд", max_length=10, blank=True)
    floor = models.CharField("Этаж", max_length=10, blank=True)
    apartment = models.CharField("Квартира", max_length=10, blank=True)
    comment = models.TextField("Комментарий", blank=True)

    # Временные метки
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    # Статус и оплата
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    is_paid = models.BooleanField("Оплачено", default=False)

    # Стоимость
    delivery_cost = models.DecimalField(
        "Стоимость доставки",
        max_digits=8,
        decimal_places=2,
        default=150
    )
    total_cost = models.DecimalField("Итоговая стоимость", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Автоматический расчет общей стоимости при сохранении"""
        cart_total = self.cart.total_price if self.cart else 0
        self.total_cost = cart_total + self.delivery_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.id} - {self.get_status_display()}"