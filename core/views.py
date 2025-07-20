from django.shortcuts import render, get_object_or_404

from orders.models import Cart
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
    popular_products = Product.objects.filter(
        is_active=True,
        is_popular=True
    ).select_related('category')[:8]  # Добавляем select_related для оптимизации

    return render(request, 'core/index.html', {
        'popular_products': popular_products,
        'cart': get_cart(request)
    })


def menu_view(request):
    categories = Category.objects.filter(is_active=True).exclude(slug='').order_by('order')
    return render(request, 'core/menu.html', {
        'categories': categories,
        'cart': get_cart(request)
    })


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')  # Добавляем select_related
    
    sort = request.GET.get('sort')
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')
    elif sort == 'popular':
        products = products.filter(is_popular=True)

    return render(request, 'core/category.html', {
        'category': category,
        'products': products,
        'cart': get_cart(request)
    })