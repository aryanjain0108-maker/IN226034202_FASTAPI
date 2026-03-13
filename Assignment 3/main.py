from fastapi import FastAPI, HTTPException

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

@app.post("/products", status_code=201)
def add_product(name: str, price: int, category: str, in_stock: bool):
    for p in products:
        if p["name"].lower() == name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")
    new_id = max(p["id"] for p in products) + 1
    product = {"id": new_id, "name": name, "price": price, "category": category, "in_stock": in_stock}
    products.append(product)
    return {"message": "Product added", "product": product}

@app.put("/products/{product_id}")
def update_product(product_id: int, price: int | None = None, in_stock: bool | None = None):
    for p in products:
        if p["id"] == product_id:
            if price is not None:
                p["price"] = price
            if in_stock is not None:
                p["in_stock"] = in_stock
            return {"message": "Product updated", "product": p}
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/audit")
def audit_products():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p["in_stock"])
    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]
    total_stock_value = sum(p["price"] * 10 for p in products if p["in_stock"])
    most_expensive = max(products, key=lambda x: x["price"])
    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }

@app.put("/products/discount")
def discount_products(category: str, discount_percent: int):
    updated = []
    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append({"name": p["name"], "price": p["price"]})
    if not updated:
        return {"message": "No products found in this category"}
    return {"updated_count": len(updated), "products": updated}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")
