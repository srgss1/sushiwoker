from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_resized import ResizedImageField


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL-адрес", max_length=100, unique=True, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    image = models.ImageField("Изображение", upload_to='categories/', blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)  # 1. Однократное создание slug
            unique_slug = base_slug
            counter = 1

            # 2. Проверка уникальности с временной переменной
            while Category.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug  # 3. Однократное присвоение

        # 4. Добавляем проверку для существующих записей
        elif Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            raise ValueError(f"Slug '{self.slug}' уже существует для другой категории")
        
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

    # Основное изображение с автоматической оптимизацией
    image = ResizedImageField(
        "Изображение",
        upload_to='products/',
        size=[1200, 800],  # Максимальный размер
        quality=85,  # Качество сжатия
        crop=['middle', 'center'],  # Точка обрезки
        force_format='WEBP',  # Современный формат
        blank=True,
        null=True
    )

    # Изображения для разных разрешений
    image_small = models.ImageField("Маленькое изображение", upload_to='products/small/', blank=True, null=True)
    image_medium = models.ImageField("Среднее изображение", upload_to='products/medium/', blank=True, null=True)
    
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
        # Генерация slug
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        # Сохраняем объект, чтобы получить доступ к файлу изображения
        super().save(*args, **kwargs)

        # Генерация ресайзов изображений
        if self.image:
            # Открываем основное изображение
            img = Image.open(self.image.path)

            # Маленький размер (480px по ширине, высота автоматически)
            img_small = img.copy()
            img_small.thumbnail((480, 480))
            buffer_small = BytesIO()

            # Сохраняем в формате WEBP
            img_small.save(buffer_small, format='WEBP')

            # Сохраняем в поле image_small
            self.image_small.save(
                f"{self.slug}_small.webp",
                ContentFile(buffer_small.getvalue()),
                save=False
            )

            # Средний размер (768px по ширине)
            img_medium = img.copy()
            img_medium.thumbnail((768, 768))
            buffer_medium = BytesIO()
            img_medium.save(buffer_medium, format='WEBP')

            # Сохраняем в поле image_medium
            self.image_medium.save(
                f"{self.slug}_medium.webp",
                ContentFile(buffer_medium.getvalue()),
                save=False
            )

            # Сохраняем изменения
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def image_aspect_ratio(self):
        """Возвращает соотношение сторон в процентах для padding-bottom"""
        if self.image and self.image.width and self.image.height:
            return (self.image.height / self.image.width) * 100
        return 66.66  # Значение по умолчанию 3:2 (200/300*100 ≈ 66.66)
