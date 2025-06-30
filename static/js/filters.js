// static/js/filters.js
function filterProducts(category) {
    const products = document.querySelectorAll('.product-card');
    
    products.forEach(product => {
        if (category === 'all' || product.dataset.category === category) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Сортировка
function sortProducts(criteria) {
    const container = document.querySelector('.product-grid');
    const products = [...container.children];
    
    products.sort((a, b) => {
        const priceA = parseFloat(a.dataset.price);
        const priceB = parseFloat(b.dataset.price);
        
        if (criteria === 'price-asc') return priceA - priceB;
        if (criteria === 'price-desc') return priceB - priceA;
        return 0;
    });
    
    // Перезаполняем контейнер
    container.innerHTML = '';
    products.forEach(product => container.appendChild(product));
}