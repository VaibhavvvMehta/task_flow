"""
Handles authentication API endpoints and page rendering.
"""

import time

from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


def set_auth_cookies(response, tokens):
    """Set JWT tokens as httpOnly cookies — JS cannot read these."""
    response.set_cookie(
        key='access_token', value=tokens['access'], path='/',
        httponly=True, samesite='Lax', secure=False,
    )
    response.set_cookie(
        key='refresh_token', value=tokens['refresh'], path='/',
        httponly=True, samesite='Lax', secure=False,
    )
    return response


# API Views 

class LoginView(APIView):
    """POST /api/v1/auth/login/ — returns JWT tokens + role for redirect."""

    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email')
        password = request.data.get('password')

        if email is None or email.strip() == '':
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password is None or password.strip() == '':
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Normalize email — strip whitespace and lowercase
        email = email.strip().lower()

        # Find all users matching this email (case-insensitive)
        candidates = User.objects.filter(email__iexact=email).order_by('id')

        if not candidates.exists():
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Try each candidate until one authenticates
        user = None
        for candidate in candidates:
            authed = authenticate(request, username=candidate.username, password=password)
            if authed is not None:
                user = authed
                break

        if user is None:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account deactivated. Contact your admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens   = get_tokens_for_user(user)
        response = Response({
            'message': 'Login successful',
            'role':    user.role,
            'user': {
                'id':         user.id,
                'email':      user.email,
                'full_name':  f'{user.first_name} {user.last_name}'.strip(),
                'role':       user.role,
                'department': user.department,
            }
        }, status=status.HTTP_200_OK)

        return set_auth_cookies(response, tokens)


class LogoutView(APIView):
    """POST /api/v1/auth/logout/-
       1. blacklist the JWTs in Redis.
       2. delete token cookies from the browser.
    """

    permission_classes = [AllowAny]

    def _blacklist_token(self, raw_token, token_class):
        """Store token JTI in Redis until the token naturally expires."""
        try:
            token = token_class(raw_token)
            jti   = token['jti']
            ttl   = max(int(token['exp'] - time.time()), 0)
            if ttl > 0:
                cache.set(f'blacklist:jti:{jti}', '1', timeout=ttl)
        except Exception:
            pass  # invalid/expired token — nothing to blacklist

    def post(self, request):
        self._blacklist_token(request.COOKIES.get('access_token'),  AccessToken)
        self._blacklist_token(request.COOKIES.get('refresh_token'), RefreshToken)

        response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token',  path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


class TokenRefreshView(APIView):
    """POST /api/v1/auth/token/refresh/ — issues new access token using refresh token."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response(
                {'error': 'Refresh token not found. Please log in again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            jti = refresh['jti']
            if cache.get(f'blacklist:jti:{jti}'):
                return Response(
                    {'error': 'Session expired. Please log in again.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            response = Response(
                {'message': 'Token refreshed'},
                status=status.HTTP_200_OK
            )
            response.set_cookie(
                key='access_token', value=str(refresh.access_token), path='/',
                httponly=True, samesite='Lax', secure=False,
            )
            return response

        except Exception:
            return Response(
                {'error': 'Session expired. Please log in again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    """
    GET  /api/v1/auth/me/ — full profile of logged-in user
    PATCH /api/v1/auth/me/ — update own first_name, last_name only
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id':          user.id,
            'email':       user.email,
            'username':    user.username,
            'first_name':  user.first_name,
            'last_name':   user.last_name,
            'full_name':   f'{user.first_name} {user.last_name}'.strip(),
            'role':        user.role,
            'department':  user.department,
            'is_active':   user.is_active,
            'date_joined': user.date_joined,
        })

    def patch(self, request):
        user           = request.user
        allowed_fields = ['first_name', 'last_name']
        updated_fields = []

        for field in allowed_fields:
            value = request.data.get(field)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(user, field, value)
                updated_fields.append(field)

        if not updated_fields:
            return Response(
                {'message': 'No fields to update'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.save()
        return Response({
            'message':   f'Updated: {", ".join(updated_fields)}',
            'full_name': f'{user.first_name} {user.last_name}'.strip(),
        }, status=status.HTTP_200_OK)


# Frontend Views

class LoginPageView(View):
    """Renders the login HTML page. Redirects to dashboard if already logged in."""

    def get(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            try:
                AccessToken(raw_token)  # raises TokenError if expired or invalid
                return redirect('dashboard')
            except TokenError:
                pass  # expired/invalid — fall through to login form
        response = render(request, 'auth/login.html')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        return response


class DashboardView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'dashboard.html')
    
class EmployeeListView(APIView):
    """GET /api/v1/users/employees/ — employees in manager's department"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['manager', 'admin']:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        if request.user.role == 'admin':
            employees = User.objects.filter(role='employee', is_active=True).order_by('first_name')
        else:
            employees = User.objects.filter(
                manager=request.user,
                role='employee',
                is_active=True,
            ).order_by('first_name')

        data = [{
            'id':         emp.id,
            'full_name':  f'{emp.first_name} {emp.last_name}'.strip(),
            'email':      emp.email,
            'department': emp.department,
        } for emp in employees]

        return Response(data)


class ProfilePageView(View):
    """Renders the user profile page — all roles."""
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'profile.html')

class HierarchyPageView(View):
    """Renders the hierarchy / org-chart page — all roles."""
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'hierarchy.html')


class HierarchyView(APIView):
    """
    GET /api/v1/users/hierarchy/
    Returns department-based org chart data.
    ?scope=team   (default) — current user's department only
    ?scope=company          — all departments (admin always gets company)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.query_params.get('scope', 'team')

        # Admins always see the full company
        if request.user.role == 'admin':
            scope = 'company'

        result = []

        if scope == 'company':
            # One block per manager, each showing their own direct reports
            managers = (
                User.objects.filter(role='manager', is_active=True)
                .order_by('department', 'first_name', 'last_name')
            )
            for mgr in managers:
                employees = (
                    User.objects.filter(manager=mgr, role='employee', is_active=True)
                    .order_by('first_name', 'last_name')
                )
                result.append({
                    'department': mgr.department or '',
                    'manager': {
                        'id':        mgr.id,
                        'full_name': f'{mgr.first_name} {mgr.last_name}'.strip(),
                        'email':     mgr.email,
                    },
                    'employees': [{
                        'id':        emp.id,
                        'full_name': f'{emp.first_name} {emp.last_name}'.strip(),
                        'email':     emp.email,
                    } for emp in employees],
                })

        else:
            # Team scope — show the manager the requesting user reports to
            if request.user.role == 'manager':
                mgr = request.user
            else:
                # Employee sees the hierarchy of their own assigned manager
                mgr = request.user.manager

            if mgr:
                employees = (
                    User.objects.filter(manager=mgr, role='employee', is_active=True)
                    .order_by('first_name', 'last_name')
                )
                result.append({
                    'department': mgr.department or '',
                    'manager': {
                        'id':        mgr.id,
                        'full_name': f'{mgr.first_name} {mgr.last_name}'.strip(),
                        'email':     mgr.email,
                    },
                    'employees': [{
                        'id':        emp.id,
                        'full_name': f'{emp.first_name} {emp.last_name}'.strip(),
                        'email':     emp.email,
                    } for emp in employees],
                })

        return Response(result)