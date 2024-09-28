import pytest
from fastapi.testclient import TestClient
from app.get_session_maker import get_session_maker
from app.main import app
from app.start_DB import OrderStatus
from app.functions_for_BD import create_new_product, delete_product, get_product_by_id, delete_order
from app.get_session_maker import get_session_maker
from datetime import datetime

SessionLocal = get_session_maker()

@pytest.fixture
def fixture_delete_product():
    """
    Возвращает TestClient и словарь для храненния айди продукта.
    После чего удаляет созданный в тесте продукт.
    """
    client = TestClient(app)
    product_id = { "id": -1}
    yield client, product_id
    
    #Удаление продукта
    with SessionLocal() as session:
        delete_product(session, product_id["id"])

def test_create_product(fixture_delete_product):
   #Тест создания продукта
    new_product = {
        "name": "Test Product",
       "description": "11112",
       "price": 10.00,
        "stock_quantity": 100
    }
    client, product_id = fixture_delete_product
    response = client.post("/products", json=new_product)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["name"] == "Test Product"
    assert json_response["description"] == "11112"
    assert json_response["price"] == 10.00
    assert json_response["stock_quantity"] == 100

    #Возвращение id продукта 
    product_id["id"] = json_response["id"]

def test_get_product(fixture_delete_product):
    #Тест получения несуществующего продукта
    client, _ = fixture_delete_product
    response = client.get("/products/999999999")
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["message"] == "Продукт не найден"

@pytest.fixture
def fixture_create_product():
    """
    Создает продукт в таблицу для изменения и
    Возвращает TestClient с айди созданного продукта.
    После чего удаляет созданный в тесте продукт.
    """
    with SessionLocal() as session:
        poduct_id = create_new_product(session, "Product test 2", "test 2", 10000.222, 800)

    client = TestClient(app)
    yield client, poduct_id

    with SessionLocal() as cleaning_session:
        delete_product(cleaning_session, poduct_id)

def test_get_product_2(fixture_create_product):
    #Тест получения существующего продукта
    client, product_id = fixture_create_product
    response = client.get(f"/products/{product_id}")
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["name"] == "Product test 2"

def test_put_info_product(fixture_create_product):
    #Тест изменения информации о продукте
    new_info_product = {
        "name": "Test Product",
        "description": "",
        "price": 10.00,
        "stock_quantity": 100
    }
    client, product_id = fixture_create_product
    response = client.put(f"/products/{product_id}", json=new_info_product)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["name"] == "Test Product"
    assert json_response["description"] == ""
    assert json_response["price"] == 10.00
    assert json_response["stock_quantity"] == 100

@pytest.fixture
def fixture_create_order():
    """
    Саздает два продукта для проверки изменения количества на складе,
    Возвращает Client, айди продуктов и словарь для хранения созданного в тесте заказа.
    После теста удаляет заказ и продукты.
    """
    #Создание продуктов
    with SessionLocal() as session:
        poduct_id1 = create_new_product(session, "Product test 31", "test 3", 10000.222, 800)
        poduct_id2 = create_new_product(session, "Product test 31", "test 3", 10000.222, 800)

    client = TestClient(app)
    order_id = {"order": -1} #Для передачи Id заказа 
    yield client, poduct_id1, poduct_id2, order_id

    #Удаление заказа и продуктов
    with SessionLocal() as cleaning_session:
        delete_product(cleaning_session, poduct_id1)
        delete_product(cleaning_session, poduct_id2)
        delete_order(cleaning_session, order_id["order"])

def test_post_create_order(fixture_create_order):
    #Тест создания заказа
    client, product_id1, product_id2, order_id  = fixture_create_order
    order_date = datetime.now()
    new_order = {
        "order":{
            "date": order_date.isoformat(),
            "status": "в процессе"
        },
        "products":[
            {"product_id": product_id1,
            "quantity": 1},
            {"product_id": product_id2,
            "quantity": 800}
        ]
    }
    response = client.post("/orders", json=new_order)
    json_response = response.json()
    #Проверка заказа, как ответ запроса
    assert response.status_code == 200
    assert json_response["date"] == order_date.isoformat()
    assert json_response["status"] ==  OrderStatus.in_progress.value

    #Првека уменьшения товара из бд
    with SessionLocal() as session:
        product1 = get_product_by_id(session, product_id1)
        product2 = get_product_by_id(session, product_id2)
        assert product1.stock_quantity == 799
        assert product2.stock_quantity == 0

    #Передача Id заказа в фикстуру для удаления заказа
    order_id["order"] = json_response["id"]