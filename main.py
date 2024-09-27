from fastapi import FastAPI, HTTPException
from functions_for_BD import create_new_product, create_new_order,  get_products, get_orders, get_product_by_id, get_order_by_id, delete_product, update_product_info, update_order_status
from typing import List
from get_session_maker import get_session_maker
from pydantic_models import ProductResponse, ProductRequest, OrderResponse, OrderRequest, ProductInOrderRequest, OrderStatusRequest

app = FastAPI()

#Создание фабрики сессий
SessionLocal = get_session_maker()

@app.get("/products")
async def send_products():
    """
    Запрос для получения списка всех продуктов.
    Ответ: 200 ОК Список продуктов или сообщение "Нет товаров"
    """
    with SessionLocal() as session:
        products_list = get_products(session) #Получение списка продуктов

        if len(products_list) == 0:
            return {"message":"Товаров нет"}
        else:
            return products_list

@app.get("/orders", response_model=List[OrderResponse])
async def send_orders():
    """
    Запрос для получения списка всех заказов.
    Ответ: 200 ОК Список заказов или сообщение "Заказов нет"
    """
    with SessionLocal() as session:
        orders_list = get_orders(session) #Получение списка заказов

        if len(orders_list) == 0:
            return {"message":"Заказов нет"}
        else:
            return orders_list

@app.get("/products/{product_id}")
async def send_product(product_id: int):
    """
    Запрос для получения продукта по ID.
    ID передается в параметрах пути.
    Ответ: 200 ОК продукт или сообщение "Продукт не найден"
    """
    with SessionLocal() as session:
        product = get_product_by_id(session, product_id) #Получение продукта 

        if product == None:
            return {"message" : "Продукт не найден"}
        else: 
            return product
    
@app.get("/orders/{order_id}")
async def send_order(order_id: int):
    """
    Запрос для получения заказа по ID.
    ID передается в параметрах пути.
    Ответ: 200 ОК заказ или сообщение "Заказ не найден"
    """
    with SessionLocal() as session:
        order = get_order_by_id(session, order_id) #Получение заказа 

        if order == None:
            return {"message" : "Заказ не найден"}
        else: 
            return order
    
@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductRequest):
    """
    Запрос для получения создания продукта.
    Информация о продукте передается в параметрах запроса.
    Ответ: 200 ОК информацию о товаре или ошибку
    """
    with SessionLocal() as session:
        product_id = create_new_product(session, product.name, product.description, product.price, product.stock_quantity) #Создание заказа

        if product_id > -1:
            return get_product_by_id(session, product_id)
        else:
            raise HTTPException(status_code=504, detail="Ошибка базы данных")


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product: ProductRequest, product_id: int):
    """
    Запрос для изменения продукта.
    ID продукта передается в параметрах пути.
    Информация о продукте передается в параметрах запроса.
    Ответ: 200 ОК информацию о товаре или ошибку
    """
    with SessionLocal() as session:
        result_update = update_product_info(session, product_id, product.name, product.description, product.price, product.stock_quantity) #Изменение каждого параметра товара

        if result_update == "Success":
            return get_product_by_id(session, product_id)
        else:
            raise HTTPException(status_code=404, detail=result_update)
        
@app.delete("/products/{product_id}")
async def delete_product_from_db(product_id: int):
    """
    Запрос для удаления продукта.
    ID продукта передается в параметрах пути.
    Ответ: 200 ОК сообщение об успешном удалении продукта. 404 в случае если нет товара или произошла ошибка.
    """
    with SessionLocal() as session:
        result_delete = delete_product(session, product_id)#Удаление товара

        if result_delete == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        elif result_delete == -1:
            raise HTTPException(status_code=504, detail="Database Error")
        else:
            return {"message": f"Product {product_id} deleted"}

@app.patch("/orders/{order_id}", response_model=OrderResponse)
def update_order_status_db(status: OrderStatusRequest, order_id: int):
    """
    Запрос для обновления статуса заказа.
    ID заказа передается в параметрах пути.
    Новый стату передается в параметрах запроса.
    Ответ: 200 ОК информация о заказе, 404 в случае если нет товара или произошла ошибка.
    """
    with SessionLocal() as session:
        result_update_status = update_order_status(session, order_id, status.status)

        if  result_update_status == "Success":
            return get_order_by_id(session, order_id)
        else:
            raise HTTPException(status_code=404, detail=result_update_status)
        
@app.post("/orders", response_model=OrderResponse)
async def create_order_db(order: OrderRequest, products: List[ProductInOrderRequest]):
    """
    Запрос для создания заказа.
    Информация о заказе и продуктах в заказе передаются в параметрах запроса.
    Ответ: 200 ОК информацию о заказе, 404 в случае если нехватает продуктов или произошла ошибка.
    """
    with SessionLocal() as session:
        str_result_created, int_result_created, id_order = create_new_order(session, order.date, order.status, products) #Добавление заказа. Функция возвращает ID добавленного заказа

        if int_result_created == 0:
            return get_order_by_id(session, id_order)
        else:
            raise HTTPException(status_code=404, detail=str_result_created)

