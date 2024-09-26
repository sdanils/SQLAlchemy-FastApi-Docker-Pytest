from fastapi import FastAPI, HTTPException
from functionsBD import create_new_product, create_new_order, create_new_order_item, get_products, get_orders, get_product_by_id, get_order_by_id, delete_product, update_product_info, update_order_status
from typing import List
from get_session_maker import get_session_maker
from pydantic_models import ProductResponse, ProductRequest, OrderResponse, OrderRequest, ProductInOrderRequest, OrderStatusRequest

app = FastAPI()

#Создание фабрики сессий
SessionLocal = get_session_maker()

@app.get("/")
async def read_root():
    """
    Получает список всех продуктов из базы данных.
    """
    return {"message" : "Hello!"}

@app.get("/products")
async def get_products():
    """
    Получает список всех продуктов из базы данных.
    """
    with SessionLocal() as session:
        products_list = get_products(session) #Получение списка продуктов

        if len(products_list) == 0:
            return {"message":"Товаров нет"}
        else:
            return products_list

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders():
    """
    Получает список всех заказов из базы данных.
    """
    with SessionLocal() as session:
        orders_list = get_orders(session) #Получение списка заказов

        if len(orders_list) == 0:
            return {"message":"Товаров нет"}
        else:
            return orders_list

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """
    Получает продукта по id.
    """
    with SessionLocal() as session:
        product = get_product_by_id(session, product_id) #Получение продукта 

        if product == None:
            return {"message" : "Продукт не найден"}
        else: 
            return product
    
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """
    Получает заказа по id.
    """
    with SessionLocal() as session:
        order = get_order_by_id(session, order_id) #Получение заказа 

        if order == None:
            return {"message" : "Заказ не найден"}
        else: 
            return order
    
@app.post("/products")
async def create_product(product: ProductRequest):
    """
    Создание продукта.
    Запрос принимает Json данные формата ProductRequest
    """
    with SessionLocal() as session:
        product_id = create_new_product(session, product.name, product.description, product.price, product.stock_quantity) #Создание заказа

        if product_id > -1:
            return {"message" : f"Created {product_id} product"}
        else:
            return {"massege" : "Database error"}


@app.put("/products/{product_id}")
async def update_product(product: ProductRequest, product_id: int):
    """
    Полная замена существующего товара.
    Возвращает статус операции.
    """
    with SessionLocal() as session:
        result_update = update_product_info(session, product_id, product.name, product.description, product.price, product.stock_quantity) #Изменение каждого параметра товара

        return {"massage": result_update}
        
@app.delete("/products/{product_id}")
async def delete_prodcut(product_id: int):
    """
    Удаление товара по ID
    Возвращает ошибки 404 в случае ошибки базы данных или не существовании предмета.
    Возвращает сообщение 
    """
    with SessionLocal() as session:
        result_delete = delete_product(session, product_id)#Удаление товара

        if result_delete == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        elif result_delete == -1:
            raise HTTPException(status_code=404, detail="Database Error")
        else:
            return {"message": f"Product {product_id} deleted"}

@app.patch("/orders/{order_id}")
def update_order_status(status: OrderStatusRequest, order_id: int):
    """
    Обновление статуса заказа по ID
    
    """
    with SessionLocal() as session:
        result_update_status = update_order_status(session, order_id, status.status)

        if  result_update_status == "Success":
            return {"message": "Order updated success"}
        else:
            raise HTTPException(status_code=404, detail=result_update_status)
        
@app.post("/orders")
async def create_product(order: OrderRequest, products: List[ProductInOrderRequest]):
    """
    Создание заказа и товаров в заказе.
    По умолчанию принимается, что  все товары в заказе ProductInOrderRequest принадлежат создаваемому OrderRequest
    
    """
    with SessionLocal() as session:
        result_created_order = create_new_order(session, order.date, order.status, products) #Добавление заказа. Функция возвращает ID добавленного заказа

        if result_created_order == -1:
            raise HTTPException(status_code=404, detail="Error created order")
        
        return 
       