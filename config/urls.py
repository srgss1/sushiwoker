from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core.views import index, menu_view, category_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),  # Главная страница
    path('menu/', menu_view, name='menu'),  # Страница меню
    path('menu/<slug:slug>/', category_view, name='category_detail'),  # Страница категории
    path('orders/', include('orders.urls')),  # Подключаем URL-адреса приложения orders
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)