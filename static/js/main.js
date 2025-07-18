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

document.addEventListener('DOMContentLoaded', function() {
    // ============= Мобильное меню =============
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mainNav = document.getElementById('mainNav');
    
    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            mainNav.classList.toggle('active');
            document.body.classList.toggle('no-scroll');
        });
        
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
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const category = this.dataset.category || 'all';
                
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
                    case 'price-asc': return priceA - priceB;
                    case 'price-desc': return priceB - priceA;
                    case 'popular': 
                        const popularA = a.dataset.popular === 'true' ? 1 : 0;
                        const popularB = b.dataset.popular === 'true' ? 1 : 0;
                        return popularB - popularA;
                    default: return 0;
                }
            });
            
            container.innerHTML = '';
            products.forEach(product => container.appendChild(product));
        });
    }
    
    // ============= Добавление в корзину (с контролами количества) =============
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', async function() {
            const productId = this.dataset.product;
            const button = this;
            
            console.log('CSRF Token:', getCookie('csrftoken'));
            
            button.textContent = 'Добавляем...';
            button.disabled = true;
            
            try {
                const response = await fetch(`/orders/cart/add/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    credentials: 'include'
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                button.style.display = 'none';
                
                const controls = document.querySelector(`.quantity-controls[data-product="${productId}"]`);
                if (controls) {
                    controls.style.display = 'flex';
                    controls.querySelector('.quantity-display').textContent = '1';
                }
                
                updateCartCounters(data.total_items);
                
            } catch (error) {
                console.error('Ошибка добавления в корзину:', error);
                button.textContent = 'Ошибка!';
                setTimeout(() => {
                    button.textContent = 'В корзину';
                    button.disabled = false;
                }, 2000);
            }
        });
    });
    
    // Управление количеством товара
    document.addEventListener('click', function(e) {
        // Увеличение количества
        if (e.target.classList.contains('quantity-btn') && e.target.classList.contains('plus')) {
            const controls = e.target.closest('.quantity-controls');
            const productId = controls.dataset.product;
            const display = controls.querySelector('.quantity-display');
            let quantity = parseInt(display.textContent) + 1;
            
            display.textContent = quantity;
            updateCartItemCount(productId, quantity);
        }
        
        // Уменьшение количества
        if (e.target.classList.contains('quantity-btn') && e.target.classList.contains('minus')) {
            const controls = e.target.closest('.quantity-controls');
            const productId = controls.dataset.product;
            const display = controls.querySelector('.quantity-display');
            let quantity = parseInt(display.textContent) - 1;
            
            if (quantity < 1) {
                removeCartItem(productId, controls);
            } else {
                display.textContent = quantity;
                updateCartItemCount(productId, quantity);
            }
        }
    });
    
    // Функция для обновления количества товара
    async function updateCartItemCount(productId, quantity) {
        try {
            const response = await fetch(`/orders/cart/update_by_product/${productId}/`, {
                method: 'POST',
                body: JSON.stringify({ quantity: quantity }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include'
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                updateCartCounters(data.total_items);
            } else {
                console.error('Server error:', data.error);
                alert(`Ошибка обновления: ${data.error}`);
            }
        } catch (error) {
            console.error('Update error:', error);
            alert('Произошла ошибка при обновлении количества');
        }
    }
    
    // Функция для удаления товара
    function removeCartItem(productId, controls) {
        fetch(`/orders/cart/remove_by_product/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                controls.style.display = 'none';
                
                const addButton = controls.closest('.product-card').querySelector('.add-to-cart');
                if (addButton) {
                    addButton.style.display = 'block';
                    addButton.textContent = 'В корзину';
                    addButton.disabled = false;
                }
                
                updateCartCounters(data.total_items);
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }
    
    // Обновление счетчиков корзины
    function updateCartCounters(count) {
        document.querySelectorAll('.cart-count').forEach(counter => {
            counter.textContent = count;
            counter.classList.add('pulse');
            setTimeout(() => counter.classList.remove('pulse'), 500);
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
    
    // ============= Обработчики для корзины =============
    // Обработчики для кнопок +/- ТОЛЬКО ДЛЯ КОРЗИНЫ
    document.querySelectorAll('.quantity-btn[data-item-id]').forEach(button => {
        button.addEventListener('click', function(e) {
            console.log(`[Frontend][Cart] Кнопка нажата: ${this.className}`);
            e.stopPropagation();
            const itemId = this.dataset.itemId;
            const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            
            if (!input) {
                console.error(`Input not found for item: ${itemId}`);
                return;
            }
            
            let quantity = parseInt(input.value);
            
            if (this.classList.contains('plus')) {
                quantity++;
            } else if (this.classList.contains('minus') && quantity > 1) {
                quantity--;
            }
            
            input.value = quantity;
            updateCartItem(itemId, quantity);
        });
    });
    
    // Функция для обновления количества товара в корзине
	function updateCartItem(itemId, quantity) {
		console.log(`[Frontend][Cart] Запрос на обновление: itemId=${itemId}, quantity=${quantity}`);
		
		const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
		if (!input) {
			console.error(`Input not found for update: ${itemId}`);
			return;
		}
		
		const originalValue = input.value;
		console.log(`[Frontend][Cart] Текущее значение: ${originalValue}, новое: ${quantity}`);
		
		// Блокируем инпут во время запроса
		input.disabled = true;
		
		fetch(`/orders/cart/update/${itemId}/`, {
			method: 'POST',
			body: JSON.stringify({ quantity: quantity }),
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken')
			}
		})
		.then(response => {
			if (response.status === 404) {
				// Товар не найден - перезагружаем корзину
				alert('Товар не найден в корзине. Корзина будет обновлена.');
				location.reload();
				return null;
			}
			return response.json();
		})
		.then(data => {
			if (!data) return; // Уже обработали 404
			
			if (data.success) {
				// Обновляем суммы в таблице
				const itemTotal = document.querySelector(`.item-total[data-item-id="${itemId}"]`);
				if (itemTotal) {
					itemTotal.textContent = data.item_total.toFixed(2) + ' ₽';
				} else {
					console.warn(`Element .item-total[data-item-id="${itemId}"] not found`);
				}
				
				// Обновляем итоговые суммы
				const subtotalEl = document.querySelector('.cart-subtotal');
				const totalEl = document.querySelector('.cart-total');
				
				if (subtotalEl && totalEl) {
					subtotalEl.textContent = data.cart_total.toFixed(2) + ' ₽';
					totalEl.textContent = (parseFloat(data.cart_total) + 150).toFixed(2) + ' ₽';
				}
				
				// Обновляем счетчик в шапке
				document.querySelectorAll('.cart-count').forEach(counter => {
					counter.textContent = data.total_items;
					counter.classList.add('pulse');
					setTimeout(() => counter.classList.remove('pulse'), 500);
				});
			} else {
				alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
				// Восстанавливаем предыдущее значение
				input.value = originalValue;
			}
		})
		.catch(error => {
			console.error('Ошибка:', error);
			alert('Произошла ошибка при обновлении количества');
			input.value = originalValue;
		})
		.finally(() => {
			if (input) input.disabled = false;
		});
	}
    
    // Обработчики для удаления товаров
    document.querySelectorAll('.remove-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const itemId = this.action.split('/').filter(Boolean).pop();
            
            if (!confirm('Удалить товар из корзины?')) {
                return;
            }
            
            const form = this;
            const submitButton = form.querySelector('button[type="submit"]');
            
            // Блокируем кнопку во время запроса
            submitButton.disabled = true;
            submitButton.textContent = 'Удаление...';
            
            fetch(form.action, {
                method: 'POST',
                body: JSON.stringify({}),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (response.status === 404) {
                    alert('Товар уже удален. Корзина будет обновлена.');
                    location.reload();
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return; // Уже обработали 404
                
                if (data.success) {
                    // Удаляем строку из таблицы
                    form.closest('tr').remove();
                    
                    // Обновляем итоговые суммы
                    document.querySelector('.cart-subtotal').textContent = data.cart_total.toFixed(2) + ' ₽';
                    document.querySelector('.cart-total').textContent = (parseFloat(data.cart_total) + 150).toFixed(2) + ' ₽';
                    
                    // Обновляем счетчик в шапке
                    document.querySelectorAll('.cart-count').forEach(counter => {
                        counter.textContent = data.total_items;
                        counter.classList.add('pulse');
                        setTimeout(() => counter.classList.remove('pulse'), 500);
                    });
                    
                    // Если корзина пуста, перезагружаем страницу
                    if (data.total_items === 0) {
                        setTimeout(() => location.reload(), 1000);
                    }
                } else {
                    alert('Ошибка при удалении товара: ' + (data.error || ''));
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при удалении товара');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.textContent = '×';
            });
        });
    });
});