document.addEventListener('DOMContentLoaded', function() {
    // ============= Мобильное меню =============
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mainNav = document.getElementById('mainNav');
    
    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', function() {
            // Анимация бургер-иконки
            this.classList.toggle('active');
            
            // Переключение видимости меню
            mainNav.classList.toggle('active');
            
            // Блокировка прокрутки тела страницы
            document.body.classList.toggle('no-scroll');
        });
        
        // Закрытие меню при клике на пункт
        document.querySelectorAll('#mainNav a').forEach(item => {
            item.addEventListener('click', () => {
                mobileMenuBtn.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.classList.remove('no-scroll');
            });
        });
    }
    
    // ============= Фильтрация продуктов =============
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');
    
    if (filterButtons.length > 0 && productCards.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Удаляем активный класс у всех кнопок
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Добавляем активный класс текущей кнопке
                this.classList.add('active');
                
                const category = this.dataset.category || 'all';
                
                // Показываем/скрываем продукты
                productCards.forEach(card => {
                    if (category === 'all' || card.dataset.category === category) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // ============= Сортировка продуктов =============
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const container = document.querySelector('.product-grid');
            const products = Array.from(container.children);
            
            products.sort((a, b) => {
                const priceA = parseFloat(a.dataset.price);
                const priceB = parseFloat(b.dataset.price);
                
                switch(this.value) {
                    case 'price-asc':
                        return priceA - priceB;
                    case 'price-desc':
                        return priceB - priceA;
                    case 'popular':
                        const popularA = a.dataset.popular === 'true' ? 1 : 0;
                        const popularB = b.dataset.popular === 'true' ? 1 : 0;
                        return popularB - popularA;
                    default:
                        return 0;
                }
            });
            
            // Перезаполняем контейнер
            container.innerHTML = '';
            products.forEach(product => container.appendChild(product));
        });
    }
    
    // ============= Добавление в корзину (обновленная версия с AJAX) =============
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    if (addToCartButtons.length > 0) {
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.dataset.product;
                const button = this;
                
                // Визуальная обратная связь
                button.textContent = 'Добавляем...';
                button.disabled = true;
                
                // Отправляем запрос на сервер
                fetch(`/orders/cart/add/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Анимация кнопки
                        button.textContent = '✓ Добавлено';
                        button.classList.add('added');
                        
                        // Обновляем счетчик корзины
                        const cartCount = document.querySelector('.cart-count');
                        if (cartCount) {
                            cartCount.textContent = data.total_items;
                            cartCount.classList.add('pulse');
                            
                            setTimeout(() => {
                                cartCount.classList.remove('pulse');
                            }, 500);
                        }
                        
                        // Восстановление кнопки через 2 секунды
                        setTimeout(() => {
                            button.textContent = 'В корзину';
                            button.disabled = false;
                            button.classList.remove('added');
                        }, 2000);
                    } else {
                        // Ошибка
                        button.textContent = 'Ошибка!';
                        setTimeout(() => {
                            button.textContent = 'В корзину';
                            button.disabled = false;
                        }, 2000);
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    button.textContent = 'Ошибка!';
                    setTimeout(() => {
                        button.textContent = 'В корзину';
                        button.disabled = false;
                    }, 2000);
                });
            });
        });
    }
    
    // ============= Плавная прокрутка =============
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Вспомогательная функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}