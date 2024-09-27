from start_DB import Product, Order, OrderItem, OrderStatus
from sqlalchemy import  Integer, String, Float, DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic_models import ProductInOrderRequest

def create_new_product(session: Session, name_product: String, description_product: String, price_product: Float, quantity: Integer) -> int:
    """
    Создание товара в таблице Product
    
    :param session: Объект сессии SQLAlchemy.
    :param name_product: Название продукта.
    :param description_product: Описание продукта.
    :param price_product: Цена продукта.
    :param quantity: Количество товара на складе.
    :return: ID созданного продукта или -1 в случае ошибки.
    """
    try:
        new_product = Product(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name=name_product,
            description=description_product,
            price=price_product,
            stock_quantity=quantity
        )

        session.add(new_product)
        session.commit()

        return new_product.id
    
    except Exception as e:
        # В случае любой ошибки при работе с базой данных возвращаем -1
        session.rollback()
        return -1


def checking_quantity(session: Session, products: List[ProductInOrderRequest]) -> int:
    """
    Проходит по списку товаров в заказе и проверяет их доступность по колличеству

    :param session: Сессия SQLAlchemy
    :param products: Список товаров в заказе
    :return: Id нехватающего товара или -1
    """
    for product in products:
        ex_product = get_product_by_id(session, product.product_id) #Получаем экземпляр товара
        if ex_product:
            if ex_product.stock_quantity < product.quantity:#Проверка колличества
                return product.product_id #Если нехватка товара, вернет его ID
        else: 
            return -2
    return -1
    

def create_new_order(session: Session, date_order: DateTime, status: OrderStatus, products: List[ProductInOrderRequest]) -> tuple[str, int, Optional[int]]:
    """
    Создание нового заказа в таблице Order.
    1. Проверяется доступность всех товаров.
    2. Добавляется заказ.
    3.1 Добавляются все элементы ProductInOrderRequest
    3.2 Меняется значение количества доступного товара

    :param session: Объект сессии SQLAlchemy.
    :param date_order: Дата заказа
    :param status: Статус заказа
    :param products: Список товаров для добавления в заказ
    :return: ID созданного заказа с сообщением Succes или код ошибки и сообщение об ошибке.
    """
    #Проверка колличетсва товара
    result_checking = checking_quantity(session, products)
    if result_checking != -1:
        return f"There is not enough product with ID {result_checking}", result_checking, None
    elif result_checking == -2:
        return f"Uncorrect product id", result_checking, None

    #Добавление заказа и товаров в заказ
    try:
        #Создание заказа
        new_order = Order(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            date=date_order,  
            status=status
        )
        session.add(new_order)
        session.flush()

        for product in products:
            #Создание запаиси в таблицу OrderItem
            new_order_item = OrderItem(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                order_id= new_order.id,    
                product_id= product.product_id,
                quantity= product.quantity          
            )
            session.add(new_order_item)

            #Изменение количества товара
            ex_product = get_product_by_id(session, product.product_id) #Получаем экземпляр товара
            ex_product.stock_quantity -= new_order_item.quantity
            
        session.commit()
        return "Success", 0, new_order.id
    
    except SQLAlchemyError as e:
        # В случае любой ошибки при работе с базой данных возвращает текст ошибки
        session.rollback()
        return f"Error: {e}", -1, None
    

def get_products(session: Session) -> List[Product]:
    """
    Получение всех продуктов из базы данных.

    :param session: Объект сессии SQLAlchemy.
    :return: Список объектов Product.
    """
    # Запрос всех объектов Product из базы данных
    products = session.query(Product).all() 
    return products


def get_orders(session: Session) -> List[Order]:
    """
    Получение всех заказов из базы данных.

    :param session: Объект сессии SQLAlchemy.
    :return: Список объектов Order.
    """
    # Запрос всех объектов Product из базы данных
    orders = session.query(Order).all() 
    return orders


def get_product_by_id(session: Session, id_product: Integer) -> Optional[Product]:
    """
    Получение продукта по ID из таблицы Product

    :param session: Объект сессии SQLAlchemy.
    :param id_product: ID обьекта в Product, который нужно вернуть
    :return: объект Product.
    """
    #Фильтрация всех продуктов по айди и получение первого
    product = session.query(Product).filter(Product.id == id_product).first()
    return product


def get_order_by_id(session: Session, id_order: Integer) -> Optional[Order]:
    """
    Получение закакза по ID из таблицы Order

    :param session: Объект сессии SQLAlchemy.
    :param id_order: ID обьекта в Order, который нужно вернуть
    :return: обьект Order
    """
    #Фильтрация всех заказ по айди и получение первого
    order = session.query(Order).filter(Order.id == id_order).first()
    return order


def delete_product(session: Session, id_product: Integer) -> int:
    """
    Удаляет продукт из базы данных по его ID, с удалением всех связанных запесей в таблице OrderItem
    ?Теряются данные о составе заказа?

    :param session: Объект сессии SQLAlchemy.
    :param id_product: ID продукта, который нужно удалить.
    :return: 1 если продукт удален. 0 если продукт не найден. -1 если произошла ошибка
    """
    product = session.query(Product).filter(Product.id == id_product).first() 
    if product:
        try:
            # Удаление всех зависимых записей в OrderItem
            order_items = session.query(OrderItem).filter(OrderItem.product_id == product.id).all()
            for order_item in order_items:
                session.delete(order_item)
            # Удаление самого продукта
            session.delete(product)

            session.commit()

            return 1
        except SQLAlchemyError as e:
            session.rollback()
            return -1
    return 0


def update_product_info(session: Session, id_product: Integer, new_name_product: Optional[String] = None, new_description_product: Optional[String] = None, new_price_product: Optional[Float] = None, new_quantity: Optional[Integer] = None) -> str:
    """
    Обновляет информацию о продукте по его ID.
    Если передается аргумент, то происходит соответствуещее изменение продукта.
    Если аргумент None, то параметр продукта не изменяется.

    Args:
        session (Session): Сессия SQLAlchemy для взаимодействия с базой данных.
        id_product (Integer): ID продукта для обновления.
        new_name_product (Optional[String], optional): Новое имя продукта. 
        new_description_product (Optional[String], optional): Новое описание продукта. 
        new_price_product (Optional[Float], optional): Новая цена продукта.
        new_quantity (Optional[Integer], optional): Новое количество на складе.

    Returns:
        String: Строка с информацией о результате работы функции.
    """

    product = session.query(Product).filter(Product.id == id_product).first()

    if product: #Если продукт найден выполняется обновление данных
        current_update_at  = product.updated_at # Сохранение времени изменения для оптимистической блокировки данных

        if new_name_product is not None:
            product.name = new_name_product
        if new_description_product is not None:
            product.description = new_description_product
        if new_price_product is not None:
            product.price = new_price_product
        if new_quantity is not None:
            product.stock_quantity = new_quantity

        try:  # Обработка исключений
            if current_update_at == product.updated_at: #Проверка изменения данных
                session.commit()
                return "Success"
            else:
                return "Integrity error"
        except Exception as e:  # Обработка всех исключений
            session.rollback()
            return f"Error: {e}"

    else:
        return "The product is not missing"
    

def update_order_status(session: Session, id_order: Integer, new_status: OrderStatus) -> str:
    """
    Обновляет статус заказа по ID.

    Args:
        session (Session): Сессия SQLAlchemy для взаимодействия с базой данных.
        id_order (Integer): ID заказа для обновления.
        new_status  OrderStatus: Новый статус заказа. 

    Returns:
        String: Строка с информацией о результате работы функции.
    """

    order = session.query(Order).filter(Order.id == id_order).first()

    if order: #Если заказ найден выполняется обновление данных
        current_update_at  = order.updated_at # Сохранение времени изменения для оптимистической блокировки данных

        order.status = new_status

        try:  # Обработка исключений
            if current_update_at == order.updated_at: #Проверка изменения данных
                session.commit()
                return "Success"
            else:
                return "Integrity error"
        except Exception as e:  # Обработка всех исключений
            session.rollback()
            return f"Error: {e}"

    else:
        return "The product is not missing"
    



#def create_new_order_item(session: Session, order_id_: Integer, product_id_: Integer, quantity_: Integer) -> Integer:
#    """
 #   Создание элемента в таблицу OrderItem
  #  
   # :param session: Объект сессии SQLAlchemy.
    #:return:  id созданного элемента.
    #"""
    #try:
    #    new_order_item = OrderItem(
    #        created_at=datetime.now(),
    #        updated_at=datetime.now(),
    #        order_id=order_id_,    
    #        product_id=product_id_,
    #        quantity=quantity_          
    #    )

    #    session.add(new_order_item)
    #    session.commit() 
#
   #     return new_order_item.id
 #   
  #  except SQLAlchemyError as e:
   #     # В случае любой ошибки при работе с базой данных возвращаем -1
    #    session.rollback()
     #   return -1
