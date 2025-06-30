from django.shortcuts import render

from .models import Category, Product


def index(request):
    categories = Category.objects.filter(is_active=True).order_by('order')
    products = Product.objects.filter(is_active=True)  # Все активные продукты

    # Фильтрация по категории (если передана в GET-параметре)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Сортировка
    sort = request.GET.get('sort')
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')
    elif sort == 'popular':
        products = products.filter(is_popular=True)
    
    return render(request, 'core/index.html', {
        'categories': categories,
        'products': products
    })
