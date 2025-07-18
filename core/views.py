from django.shortcuts import render

from orders.models import Cart  # Добавляем импорт модели Cart
from .models import Category, Product


def get_cart(request):
    """Функция для получения корзины пользователя"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

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
        'products': products,
        'cart': get_cart(request)
    })