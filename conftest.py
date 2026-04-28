import pytest
from django.test import Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(autouse=True)
def use_in_memory_cache(settings):
    """Override Redis cache with in-memory cache so tests don't need Redis running."""
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }


@pytest.fixture
def api_client():
    client = APIClient()
    client.default_format = 'json'
    return client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def ceo_user(db):
    return User.objects.create_user(
        username='ceo_test',
        email='ceo@test.com',
        password='Test@1234',
        first_name='CEO',
        last_name='Test',
        role='ceo',
        department='Executive',
    )


@pytest.fixture
def cfo_user(db, ceo_user):
    return User.objects.create_user(
        username='cfo_test',
        email='cfo@test.com',
        password='Test@1234',
        first_name='CFO',
        last_name='Test',
        role='cfo',
        department='Executive',
        manager=ceo_user,
    )


@pytest.fixture
def cto_user(db, ceo_user):
    return User.objects.create_user(
        username='cto_test',
        email='cto@test.com',
        password='Test@1234',
        first_name='CTO',
        last_name='Test',
        role='cto',
        department='Executive',
        manager=ceo_user,
    )


@pytest.fixture
def manager_user(db, cto_user):
    return User.objects.create_user(
        username='manager_test',
        email='manager@test.com',
        password='Test@1234',
        first_name='Manager',
        last_name='Test',
        role='manager',
        department='Software',
        manager=cto_user,
    )


@pytest.fixture
def employee_user(db, manager_user):
    return User.objects.create_user(
        username='employee_test',
        email='employee@test.com',
        password='Test@1234',
        first_name='Employee',
        last_name='Test',
        role='employee',
        department='Software',
        manager=manager_user,
    )


@pytest.fixture
def employee_user_2(db, manager_user):
    return User.objects.create_user(
        username='employee2_test',
        email='employee2@test.com',
        password='Test@1234',
        first_name='Employee',
        last_name='Two',
        role='employee',
        department='Software',
        manager=manager_user,
    )


@pytest.fixture
def get_jwt_token(db):
    def _get_token(user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    return _get_token


@pytest.fixture
def authenticated_api_client(api_client, employee_user, get_jwt_token):
    tokens = get_jwt_token(employee_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    api_client.user = employee_user
    return api_client


@pytest.fixture
def manager_api_client(api_client, manager_user, get_jwt_token):
    tokens = get_jwt_token(manager_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    api_client.user = manager_user
    return api_client


@pytest.fixture
def ceo_api_client(api_client, ceo_user, get_jwt_token):
    tokens = get_jwt_token(ceo_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    api_client.user = ceo_user
    return api_client


@pytest.fixture
def cto_api_client(api_client, cto_user, get_jwt_token):
    tokens = get_jwt_token(cto_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    api_client.user = cto_user
    return api_client


@pytest.fixture
def cfo_api_client(api_client, cfo_user, get_jwt_token):
    tokens = get_jwt_token(cfo_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    api_client.user = cfo_user
    return api_client
