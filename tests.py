import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from get_session_maker import get_session_maker
from main import app
from start_DB import Product, Order, OrderItem, OrderStatus
from functions_for_BD import create_new_product, delete_product
from get_session_maker import get_session_maker

SessionLocal = get_session_maker()

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

@pytest.fixture
def client2():
    #Создается продукт в таблицу продуктов для изменения.
    #После теста его удаляет
    Local = get_session_maker()
    with Local() as session:
        poduct_id = create_new_product(session, "Product test 2", "test 2", 10000.222, 800)
        client = TestClient(app)
        yield client, poduct_id
        delete_product(session, poduct_id)

def test_create_product(client):
   #Тест создания продукта
    new_product = {
        "name": "Test Product",
       "description": "",
       "price": 10.00,
        "stock_quantity": 100
    }
    response = client.post("/products", json=new_product)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["name"] == "Test Product"
    assert json_response["description"] == ""
    assert json_response["price"] == 10.00
    assert json_response["stock_quantity"] == 100

def test_get_product(client):
    #Тест получения несуществующего продукта
    response = client.get("/products/999999999")
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["message"] == "Продукт не найден"

def test_get_product_2(client):
    #Тест получения существующего продукта
    response = client.get("/products/1")
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["name"] == "Тарелка"

def test_put_info_product(client2):
    #Тест изменения информации о продукте
    new_info_product = {
        "name": "Test Product",
        "description": "",
        "price": 10.00,
        "stock_quantity": 100
    }
    client, product_id = client2
    response = client.put(f"/products/{product_id}", json=new_info_product)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["name"] == "Test Product"
    assert json_response["description"] == ""
    assert json_response["price"] == 10.00
    assert json_response["stock_quantity"] == 100

