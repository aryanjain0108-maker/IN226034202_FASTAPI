from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from typing import List
app = FastAPI()

products = [
    {"id":1,"name":"Wireless Mouse","category":"Electronics","price":499,"in_stock":True},
    {"id":2,"name":"Notebook","category":"Stationery","price":99,"in_stock":True},
    {"id":3,"name":"USB Hub","category":"Electronics","price":799,"in_stock":False},
    {"id":4,"name":"Pen Set","category":"Stationery","price":49,"in_stock":False}
]

@app.get("/products/filter")
def filter_products(category: str = None, max_price: int = None, min_price: int = None):
    result = []
    for product in products:
        if category and product["category"] != category:
            continue
        if max_price and product["price"] > max_price:
            continue
        if min_price and product["price"] < min_price:
            continue
        result.append(product)
    return result
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name":product["name"],"price":product["price"]}
    return {"error":"Product not found"}
feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def add_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":"Feedback submitted successfully",
        "feedback":data.dict(),
        "total_feedback":len(feedback)
    }
@app.get("/products/summary")
def product_summary():
    total_products = len(products)

    in_stock_count = 0
    out_of_stock_count = 0

    for p in products:
        if p["in_stock"]:
            in_stock_count += 1
        else:
            out_of_stock_count += 1

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products":total_products,
        "in_stock_count":in_stock_count,
        "out_of_stock_count":out_of_stock_count,
        "most_expensive":{"name":most_expensive["name"],"price":most_expensive["price"]},
        "cheapest":{"name":cheapest["name"],"price":cheapest["price"]},
        "categories":categories
    }
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)
@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = None

        for p in products:
            if p["id"] == item.product_id:
                product = p
                break

        if not product:
            failed.append({"product_id":item.product_id,"reason":"Product not found"})
            continue

        if not product["in_stock"]:
            failed.append({"product_id":item.product_id,"reason":f"{product['name']} is out of stock"})
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product":product["name"],
            "qty":item.quantity,
            "subtotal":subtotal
        })

    return {
        "company":order.company_name,
        "confirmed":confirmed,
        "failed":failed,
        "grand_total":grand_total
    }
orders = []
@app.post("/orders")
def create_order(order: dict):
    order_id = len(orders)+1
    data = {"id":order_id,"order":order,"status":"pending"}
    orders.append(data)
    return data
@app.get("/orders/{order_id}")
def get_order(order_id:int):
    for order in orders:
        if order["id"]==order_id:
            return order
    return {"error":"Order not found"}
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id:int):
    for order in orders:
        if order["id"]==order_id:
            order["status"]="confirmed"
            return order
    return {"error":"Order not found"}
