from flask import Flask, render_template, redirect, url_for, session, request, flash
from decimal import Decimal
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory product catalog (clothing)
products = [
    { "id": 1, "name": "Azar Classic Tee", "price": Decimal("14.99"), "desc": "100% cotton, unisex tee", "sku": "AZ-TEE-001" },
    { "id": 2, "name": "Azar Denim Jacket", "price": Decimal("49.99"), "desc": "Stylish denim jacket", "sku": "AZ-JKT-002" },
    { "id": 3, "name": "Azar Hoodie", "price": Decimal("29.99"), "desc": "Cozy hoodie with logo", "sku": "AZ-HOD-003" },
    { "id": 4, "name": "Azar Cap", "price": Decimal("9.99"), "desc": "Adjustable cap", "sku": "AZ-CAP-004" },
]

def get_product(pid):
    return next((p for p in products if p['id'] == pid), None)

def cart_total(cart):
    total = Decimal('0.00')
    for pid_str, qty in cart.items():
        p = get_product(int(pid_str))
        if p:
            total += p['price'] * qty
    return total

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add/<int:pid>')
def add_to_cart(pid):
    p = get_product(pid)
    if not p:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))
    cart = session.get('cart', {})
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session['cart'] = cart
    flash(f"Added {p['name']} to cart.", 'success')
    return redirect(url_for('index'))

@app.route('/cart', methods=['GET','POST'])
def cart():
    if request.method == 'POST':
        cart = {}
        for k, v in request.form.items():
            if k.startswith('qty_'):
                pid = k.split('_',1)[1]
                try:
                    q = int(v)
                    if q > 0:
                        cart[pid] = q
                except:
                    pass
        session['cart'] = cart
        flash('Cart updated.', 'info')
        return redirect(url_for('cart'))

    cart = session.get('cart', {})
    items = []
    for pid_str, qty in cart.items():
        p = get_product(int(pid_str))
        if p:
            items.append({'product': p, 'qty': qty, 'subtotal': p['price'] * qty})
    total = cart_total(cart)
    return render_template('cart.html', items=items, total=total)

@app.route('/remove/<int:pid>')
def remove(pid):
    cart = session.get('cart', {})
    cart.pop(str(pid), None)
    session['cart'] = cart
    flash('Item removed.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    session.pop('cart', None)
    return render_template('checkout.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
