from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'phone', 'name', 'email',
            'address', 'entrance', 'floor', 'apartment', 'comment'
        ]
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
