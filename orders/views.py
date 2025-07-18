import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from core.models import Product
from .forms import CheckoutForm
from .models import Cart, CartItem

logger = logging.getLogger(__name__)

def get_cart(request):
    """Получает корзину пользователя"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


@ensure_csrf_cookie
@require_POST
def add_to_cart(request, product_id):
    """Добавляет товар в корзину с обработкой CSRF"""
    try:
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

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_POST
def remove_from_cart(request, item_id):
    """Удаляет товар из корзины"""
    cart = get_cart(request)
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart = cart_item.cart
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'cart_total': float(cart.total_price),
            'total_items': cart.total_items
        })
    except CartItem.DoesNotExist:
        logger.error(f"CartItem not found: item_id={item_id}, cart_id={cart.id}")
        return JsonResponse({
            'success': False,
            'error': 'Товар не найден в корзине'
        }, status=404)

@require_POST
def update_cart_item(request, item_id):
    """Обновляет количество товара в корзине"""
    logger = logging.getLogger(__name__)

    # Логирование входящего запроса
    try:
        body = request.body.decode('utf-8')
    except UnicodeDecodeError:
        body = "Binary data"
    
    logger.info(f"Получен запрос на обновление: item_id={item_id}, "
                f"POST={request.POST}, body={body}, "
                f"user={request.user}, session={request.session.session_key}")
                
    cart = get_cart(request)

    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        logger.warning(f"CartItem not found: item_id={item_id}, cart_id={cart.id}")
        return JsonResponse({
            'success': False,
            'error': 'Товар не найден в корзине'
        }, status=404)

    try:
        # Обработка JSON-данных
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        else:
            # Обработка form-data
            quantity = int(request.POST.get('quantity', 1))
            
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Количество не может быть меньше 1'
            }, status=400)

        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.total_price),
            'cart_total': float(cart.total_price),
            'total_items': cart.total_items
        })

        logger.info(f"Успешное обновление: item_id={item_id}, quantity={quantity}, "
                    f"item_total={cart_item.total_price}, cart_total={cart.total_price}")

    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка обработки количества: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Некорректное значение количества'
        }, status=400)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат запроса'
        }, status=400)

def cart_view(request):
    """Отображает страницу корзины"""
    cart = get_cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})

def checkout_view(request):
    """Обрабатывает оформление заказа"""
    cart = get_cart(request)

    if not cart.items.exists():
        return redirect('orders:cart_view')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.cart = cart
            order.total_cost = cart.total_price + 150  # Фиксированная стоимость доставки

            # Привязываем пользователя или сессию
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.session_key = request.session.session_key

            order.save()

            # Очищаем корзину
            cart.delete()

            return render(request, 'orders/order_success.html', {'order': order})
    else:
        # Предзаполняем данные, если пользователь авторизован
        initial = {}
        if request.user.is_authenticated:
            initial.update({
                'name': request.user.get_full_name() or '',
                'email': request.user.email,
            })
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart
    })


@require_POST
def update_cart_item_by_product(request, product_id):
    """Обновляет количество товара в корзине по ID продукта"""
    try:
        cart = get_cart(request)
        product = get_object_or_404(Product, id=product_id)

        # Логирование для отладки
        logger.info(f"Update request for product {product_id}")

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            logger.warning(f"CartItem not found: product_id={product_id}, cart_id={cart.id}")
            return JsonResponse({
                'success': False,
                'error': 'Товар не найден в корзине'
            }, status=404)

        try:
            # Добавим обработку пустого тела запроса
            data = json.loads(request.body) if request.body else {}
            quantity = int(data.get('quantity', 1))

            logger.info(f"Updating quantity to {quantity} for product {product_id}")

            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Количество не может быть меньше 1'
                }, status=400)

            cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({
                'success': True,
                'total_items': cart.total_items
            })

        except (ValueError, TypeError) as e:
            logger.error(f"Invalid quantity value: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Некорректное значение количества'
            }, status=400)

    except Exception as e:
        logger.exception("Unexpected error in update_cart_item_by_product")
        return JsonResponse({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }, status=500)


@require_POST
def remove_from_cart_by_product(request, product_id):
    """Удаляет товар из корзины по ID продукта"""
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'total_items': cart.total_items
        })
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Товар не найден в корзине'
        }, status=404)
