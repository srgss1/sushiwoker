from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Cart


@receiver(user_logged_in)
def merge_carts(sender, request, user, **kwargs):
    if request.session.session_key:
        # Ищем анонимную корзину
        anon_cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if anon_cart:
            # Ищем пользовательскую корзину
            user_cart, created = Cart.objects.get_or_create(user=user)
            # Переносим товары
            for item in anon_cart.items.all():
                user_item, created = user_cart.items.get_or_create(
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    user_item.quantity += item.quantity
                    user_item.save()
            anon_cart.delete()
