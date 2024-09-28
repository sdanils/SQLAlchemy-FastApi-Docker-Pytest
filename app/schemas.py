from pydantic import BaseModel
from datetime import datetime
from app.models import OrderStatus

#Создание Pydantic моделей для валидации данных при работе запросов
class ProductResponse(BaseModel):
        id: int 
        created_at: datetime
        updated_at: datetime
        name: str
        description: str
        price: float
        stock_quantity: int

        class Config:
            orm_mode = True

class ProductRequest(BaseModel):
        name: str
        description: str
        price: float
        stock_quantity: int

        class Config:
            orm_mode = True

class OrderResponse(BaseModel):
        id: int 
        created_at: datetime
        updated_at: datetime
        date: datetime
        status: OrderStatus

        class Config:
            orm_mode = True

class OrderRequest(BaseModel):
        date: datetime
        status: OrderStatus

        class Config:
            orm_mode = True

class ProductInOrderRequest(BaseModel):
        product_id: int
        quantity: int

        class Config:
            orm_mode = True

class OrderStatusRequest(BaseModel):
    status: OrderStatus