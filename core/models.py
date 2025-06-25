from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL-адрес", max_length=100, unique=True, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            # Гарантируем уникальность slug
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("URL-адрес", max_length=255, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    weight = models.PositiveIntegerField("Вес (г)", blank=True, null=True)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.CASCADE,
        related_name='products'
    )
    image = models.ImageField(
        "Изображение",
        upload_to='products/',
        default='products/placeholder.png'  # Путь к заглушке
    )
    is_popular = models.BooleanField("Популярный", default=False)
    is_new = models.BooleanField("Новинка", default=False)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.price}₽"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            # Гарантируем уникальность slug
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})  # Используем pk как идентификатор

    def clean(self):
        if not self.image:
            self.image = 'products/placeholder.png'
        super().clean()
