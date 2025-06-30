import os
import random

from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Product


class Command(BaseCommand):
    help = 'Добавляет тестовые изображения к продуктам'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Количество изображений для добавления'
        )

    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        count = options['count']

        # Путь к папке с тестовыми изображениями
        images_dir = os.path.join('static', 'images', 'products')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # Создаем тестовые изображения с помощью Faker
        image_paths = []
        for i in range(count):
            img_path = os.path.join(images_dir, f'product_{i}.jpg')
            fake.image(image_size=(400, 400), image_format='jpg', path=img_path)
            image_paths.append(img_path)
            self.stdout.write(f'Создано изображение: {img_path}')

        # Добавляем изображения к продуктам
        products = Product.objects.all()
        for product in products:
            if not product.image:
                img_path = random.choice(image_paths)
                with open(img_path, 'rb') as f:
                    product.image.save(
                        os.path.basename(img_path),
                        File(f),
                        save=True
                    )
                self.stdout.write(f'Добавлено изображение к продукту: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Успешно добавлены изображения к {products.count()} продуктам'))
