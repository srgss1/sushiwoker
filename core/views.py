from django.shortcuts import render

from .models import Category, Product


def index(request):
    categories = Category.objects.filter(is_active=True).order_by('order')
    popular_products = Product.objects.filter(is_popular=True, is_active=True)
    return render(request, 'core/index.html', {
        'categories': categories,
        'popular_products': popular_products
    })
