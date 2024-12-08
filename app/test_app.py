import pytest
from flask import session
from . import app, db
from .models import User
from . import routings

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_register(client):
    # Проверка регистрации с правильными данными
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'You have successfully registered!' in response.data
    # Проверка, что пользователь добавлен в базу данных
    user = User.query.filter_by(username='newuser').first()
    assert user is not None


def test_register_password_mismatch(client):
    # Проверка регистрации с несовпадающими паролями
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'password123',
        'password2': 'password124'
    }, follow_redirects=True)

    assert b'Passwords do not match!' in response.data


def test_login(client):
    # Сначала создаем пользователя для входа
    with app.app_context():
        user = User(username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    # Проверка входа с правильными данными
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful!' in response.data


def test_login_invalid_credentials(client):
    # Проверка входа с неправильными данными
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b'Invalid username or password!' in response.data

