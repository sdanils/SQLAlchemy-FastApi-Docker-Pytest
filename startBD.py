from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime
from sqlalchemy import event
import configparser
from get_session_maker import get_engine_db

#Создание объекта Engine
engine = get_engine_db()

# Создаём базовый класс для описания моделей
Base = declarative_base()

# Структура для описания статусов заказа
class OrderStatus(enum.Enum):
    in_progress = "в процессе"
    shipped = "отправлен"
    delivered = "доставлен"

#Определение базовой модели для базовых колонок
class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())

# Модель Product (Товар)
class Product(BaseModel):
    __tablename__ = 'products'
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price}), update_at={self.updated_at}>"

# Модель Order (Заказ)
class Order(BaseModel):
    __tablename__ = 'orders'
    
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    status: Mapped[datetime] = mapped_column(Enum(OrderStatus), default=OrderStatus.in_progress, nullable=False)

    # Связь с таблицей OrderItem
    items = relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, status={self.status}, date={self.date}), update_at={self.updated_at}>"

# Модель OrderItem (Элемент заказа)
class OrderItem(BaseModel):
    __tablename__ = 'order_items'
    
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Связи с таблицами Order и Product
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity}), update_at={self.updated_at}>"

#Обработчик изменения данных в таблице
@event.listens_for(BaseModel, 'before_update', propagate=True)
def update_timestamp_before_update(mapper, connection, target):
    # Автоматически обновляем поле updated_at на текущее время
    target.updated_at = datetime.now()

# Создание всех таблиц и обработчиков
Base.metadata.create_all(bind=engine)