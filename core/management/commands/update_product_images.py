from django.core.management.base import BaseCommand

from core.models import Product


class Command(BaseCommand):
    help = 'Updates product images with new formats and sizes'

    def handle(self, *args, **options):
        for product in Product.objects.filter(image__isnull=False):
            product.save()
            self.stdout.write(f'Updated images for: {product.name}')

        self.stdout.write(self.style.SUCCESS('Successfully updated all product images'))
