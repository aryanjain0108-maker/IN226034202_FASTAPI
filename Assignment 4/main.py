from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
app = FastAPI()
cart=[]
orders=[]
order_counter = 1
class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':  99, 'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49, 'category': 'Stationery',  'in_stock': True},
]
def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None
def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity and return total."""
    return product['price'] * quantity
def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    """Apply filters and return matching products."""
    result = products
    if category  is not None:
        result = [p for p in result if p['category'] == category]
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock  is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result
@app.post('/cart/add')
def add_to_cart(
    product_id: int = Query(..., description='Product ID to add'),
    quantity:   int = Query(1,   description='How many (default 1)'),
):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
    if not product["in_stock"]: raise HTTPException( status_code=400, detail=f"{product['name']} is out of stock" )
    if quantity < 1:
        return {'error': 'Quantity must be at least 1'}
    # Already in cart — update quantity
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            item['subtotal']  = calculate_total(product, item['quantity'])
            return {'message': 'Cart updated', 'cart_item': item}
    # New item
    cart_item = {
        'product_id':   product_id,
        'product_name': product['name'],
        'quantity':     quantity,
        'unit_price':   product['price'],
        'subtotal':     calculate_total(product, quantity),
    }
    cart.append(cart_item)
    return {'message': 'Added to cart', 'cart_item': cart_item}

@app.get('/cart')
def view_cart():
    if not cart:
        return {'message': 'Cart is empty', 'items': [], 'grand_total': 0}
    grand_total = sum(item['subtotal'] for item in cart)
    return {
        'items':       cart,
        'item_count':  len(cart),
        'grand_total': grand_total,
    }

# FIXED route /cart/checkout — must be BEFORE /cart/{product_id}
@app.post('/cart/checkout')
def checkout(checkout_data: CheckoutRequest, response: Response):
    global order_counter
    if not cart:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cart is empty — add items first'}
    placed_orders = []
    grand_total   = 0
    for item in cart:
        order = {
            'order_id':         order_counter,
            'customer_name':    checkout_data.customer_name,
            'product':          item['product_name'],
            'quantity':         item['quantity'],
            'delivery_address': checkout_data.delivery_address,
            'total_price':      item['subtotal'],
            'status':           'confirmed',
        }
        orders.append(order)
        placed_orders.append(order)
        grand_total   += item['subtotal']
        order_counter += 1
    cart.clear()
    response.status_code = status.HTTP_201_CREATED
    return {
        'message':       'Checkout successful',
        'orders_placed': placed_orders,
        'grand_total':   grand_total,
    }

# VARIABLE route — always after /cart/checkout
@app.delete('/cart/{product_id}')
def remove_from_cart(product_id: int, response: Response):
    for item in cart:
        if item['product_id'] == product_id:
            cart.remove(item)
            return {'message': f"{item['product_name']} removed from cart"}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': 'Product not in cart'}

@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}
