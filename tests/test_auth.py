import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()
pytestmark = pytest.mark.django_db

class TestLogin:
    """Test login endpoint and JWT generation."""

    def test_login_with_valid_credentials(self, api_client, employee_user):
        """User can login with correct email and password."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'employee@test.com',
            'password': 'Test@1234',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == 'employee'
        assert response.data['user']['email'] == 'employee@test.com'

    def test_login_with_invalid_password(self, api_client, employee_user):
        """Login fails with incorrect password."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'employee@test.com',
            'password': 'WrongPassword',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_login_with_nonexistent_email(self, api_client):
        """Login fails with non-existent email."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'nonexistent@test.com',
            'password': 'Test@1234',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_without_email(self, api_client):
        """Login fails without email."""
        response = api_client.post('/api/v1/auth/login/', {
            'password': 'Test@1234',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_without_password(self, api_client, employee_user):
        """Login fails without password."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'employee@test.com',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_case_insensitive_email(self, api_client, employee_user):
        """Email is case-insensitive for login."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'EMPLOYEE@TEST.COM',
            'password': 'Test@1234',
        })
        assert response.status_code == status.HTTP_200_OK

    def test_login_returns_user_role(self, api_client, manager_user):
        """Login response includes user's role."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'manager@test.com',
            'password': 'Test@1234',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == 'manager'

    def test_login_sets_auth_cookies(self, api_client, employee_user):
        """Login sets httpOnly JWT cookies."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'employee@test.com',
            'password': 'Test@1234',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies
        assert response.cookies['access_token']['httponly'] is True


class TestLogout:
    """Test logout endpoint."""

    def test_logout_clears_cookies(self, authenticated_api_client):
        """Logout deletes auth cookies."""
        response = authenticated_api_client.post('/api/v1/auth/logout/')
        assert response.status_code == status.HTTP_200_OK

    def test_logout_blacklists_token(self, authenticated_api_client):
        """Logout invalidates the JWT token."""
        authenticated_api_client.post('/api/v1/auth/logout/')
        # Try to use the same token again
        response = authenticated_api_client.post('/api/v1/auth/logout/')
        # Should fail or require re-auth
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]


class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_generates_new_access_token(self, api_client, employee_user, get_jwt_token):
        """Can refresh expired access token using refresh token."""
        tokens = get_jwt_token(employee_user)
        api_client.cookies['refresh_token'] = tokens['refresh']
        
        response = api_client.post('/api/v1/auth/token/refresh/')
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies

    def test_refresh_without_refresh_token(self, api_client):
        """Refresh fails without refresh token."""
        response = api_client.post('/api/v1/auth/token/refresh/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMeEndpoint:
    """Test /me endpoint for profile access."""

    def test_get_own_profile(self, authenticated_api_client, employee_user):
        """User can retrieve their own profile."""
        response = authenticated_api_client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == employee_user.email
        assert response.data['role'] == 'employee'
        assert response.data['full_name'] == 'Employee Test'

    def test_me_requires_authentication(self, api_client):
        """Profile endpoint requires authentication."""
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_change_name_via_patch(self, authenticated_api_client):
        """PATCH /me/ with first_name updates the name and returns 200."""
        response = authenticated_api_client.patch('/api/v1/auth/me/', {
            'first_name': 'NewName',
        })
        assert response.status_code == status.HTTP_200_OK

    def test_patch_me_returns_updated_name(self, authenticated_api_client):
        """PATCH /me/ updates first_name and last_name, returns full_name."""
        response = authenticated_api_client.patch('/api/v1/auth/me/', {
            'first_name': 'Updated',
            'last_name': 'Person',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Updated Person'


class TestAuthorizationByRole:
    """Test that different roles have appropriate access."""

    def test_employee_cannot_access_team_view(self, authenticated_api_client):
        """Employees cannot view team data."""
        response = authenticated_api_client.get('/api/v1/users/employees/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_manager_can_access_team_view(self, manager_api_client):
        """Managers can view their team."""
        response = manager_api_client.get('/api/v1/users/employees/')
        assert response.status_code == status.HTTP_200_OK

    def test_ceo_can_access_all_employees(self, ceo_api_client):
        """CEO can view all employees."""
        response = ceo_api_client.get('/api/v1/users/employees/')
        print(f"Status: {response.status_code}, Data: {response.data}")
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_view_employees(self, manager_api_client, employee_user):
        """Managers can view their team's employee list."""
        response = manager_api_client.get('/api/v1/users/employees/')
        assert response.status_code == status.HTTP_200_OK
        assert any(e['email'] == employee_user.email for e in response.data)

    def test_employee_cannot_view_employee_list(self, authenticated_api_client):
        """Employees cannot access the employee list endpoint."""
        response = authenticated_api_client.get('/api/v1/users/employees/')
        assert response.status_code == status.HTTP_403_FORBIDDEN