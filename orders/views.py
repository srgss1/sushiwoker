from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

from core.models import Product
from .forms import CheckoutForm
from .models import Cart, CartItem


def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Для анонимных пользователей используем session_key
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({
        'success': True,
        'total_items': cart.total_items
    })


@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart=get_cart(request))
    cart_item.delete()
    return redirect('cart_view')


@require_POST
def update_cart_item(request, item_id):
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            return HttpResponseBadRequest("Количество не может быть меньше 1")

        cart_item.quantity = quantity
        cart_item.save()
        return redirect('cart_view')
    except ValueError:
        return HttpResponseBadRequest("Некорректное значение количества")


def cart_view(request):
    cart = get_cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


def checkout_view(request):
    cart = get_cart(request)

    if not cart.items.exists():
        return redirect('cart_view')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.cart = cart
            order.total_cost = cart.total_price + order.delivery_cost

            # Привязываем пользователя или сессию
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.session_key = request.session.session_key

            order.save()

            # Здесь будет интеграция с Frontpad
            # send_order_to_frontpad(order)

            # Очищаем корзину
            cart.delete()

            return render(request, 'orders/order_success.html', {'order': order})
    else:
        # Предзаполняем данные, если пользователь авторизован
        initial = {}
        if request.user.is_authenticated:
            initial.update({
                'name': request.user.get_full_name(),
                'email': request.user.email,
            })
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart
    })
