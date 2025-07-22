from core.models import Category
from orders.models import Cart


def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return {'cart': cart}


def categories(request):
    return {
        'categories': Category.objects.filter(is_active=True).order_by('order')
    }
