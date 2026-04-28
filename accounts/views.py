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

EXECUTIVE_ROLES = ['ceo', 'cfo', 'cto']
ELEVATED_ROLES  = ['manager', 'ceo', 'cfo', 'cto']


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


# ── API Views ──────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """POST /api/v1/auth/login/ — returns JWT tokens + role for redirect."""

    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email')
        password = request.data.get('password')

        if email is None or email.strip() == '':
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        if password is None or password.strip() == '':
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        email = email.strip().lower()
        candidates = User.objects.filter(email__iexact=email).order_by('id')

        if not candidates.exists():
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = None
        for candidate in candidates:
            authed = authenticate(request, username=candidate.username, password=password)
            if authed is not None:
                user = authed
                break

        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Account deactivated. Contact your administrator.'}, status=status.HTTP_403_FORBIDDEN)

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
    """POST /api/v1/auth/logout/"""

    permission_classes = [AllowAny]

    def _blacklist_token(self, raw_token, token_class):
        try:
            token = token_class(raw_token)
            jti   = token['jti']
            ttl   = max(int(token['exp'] - time.time()), 0)
            if ttl > 0:
                cache.set(f'blacklist:jti:{jti}', '1', timeout=ttl)
        except Exception:
            pass

    def post(self, request):
        self._blacklist_token(request.COOKIES.get('access_token'),  AccessToken)
        self._blacklist_token(request.COOKIES.get('refresh_token'), RefreshToken)

        response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token',  path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


class TokenRefreshView(APIView):
    """POST /api/v1/auth/token/refresh/"""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'error': 'Refresh token not found. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            jti = refresh['jti']
            if cache.get(f'blacklist:jti:{jti}'):
                return Response({'error': 'Session expired. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)
            response = Response({'message': 'Token refreshed'}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token', value=str(refresh.access_token), path='/',
                httponly=True, samesite='Lax', secure=False,
            )
            return response
        except Exception:
            return Response({'error': 'Session expired. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    """
    GET   /api/v1/auth/me/  — full profile of logged-in user
    PATCH /api/v1/auth/me/  — name editing REMOVED; users cannot change their name
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
            'manager_id':  user.manager_id,
            'is_active':   user.is_active,
            'date_joined': user.date_joined,
        })

    def patch(self, request):
        # Name editing is disabled for all users
        return Response(
            {'error': 'Profile updates are not permitted.'},
            status=status.HTTP_403_FORBIDDEN,
        )


# ── Employee List ──────────────────────────────────────────────────────────────

class EmployeeListView(APIView):
    """GET /api/v1/users/employees/ — employees in the requester's scope"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ELEVATED_ROLES:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        if request.user.role in EXECUTIVE_ROLES:
            # Executives see all employees
            employees = User.objects.filter(role='employee', is_active=True).order_by('first_name')
        else:
            # Managers see only their direct reports
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


# Add To Team

class AddToTeamView(APIView):
    """
    POST /api/v1/users/team/add/
    Managers and executives can add a new user to their team.
    Body: { email, first_name, last_name, username, password }
    Manager is automatically set to the requesting user (or passed manager_id for executives).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ELEVATED_ROLES:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        email      = (request.data.get('email') or '').strip().lower()
        first_name = (request.data.get('first_name') or '').strip()
        last_name  = (request.data.get('last_name') or '').strip()
        username   = (request.data.get('username') or '').strip()
        department = (request.data.get('department') or '').strip()

        # For executives, allow specifying which manager to assign under
        manager_id = request.data.get('manager_id')
        if request.user.role in EXECUTIVE_ROLES and manager_id:
            try:
                manager = User.objects.get(id=manager_id, role='manager', is_active=True)
            except User.DoesNotExist:
                return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            manager = request.user

        if not all([email, first_name, last_name, username]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='employee',
            department=department or manager.department,
            manager=manager,
        )

        return Response({
            'message':  f'{first_name} {last_name} added to {manager.first_name} {manager.last_name}\'s team.',
            'user': {
                'id':         user.id,
                'full_name':  f'{user.first_name} {user.last_name}'.strip(),
                'email':      user.email,
                'department': user.department,
                'manager':    f'{manager.first_name} {manager.last_name}'.strip(),
            }
        }, status=status.HTTP_201_CREATED)


# Hierarchy

class HierarchyView(APIView):
    """
    GET /api/v1/users/hierarchy/
    Returns org-chart data structured around the 3-executive model.
    ?scope=team (default) | company
    Executives always get company scope.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.query_params.get('scope', 'team')

        # Executives always see the full company hierarchy
        if request.user.role in EXECUTIVE_ROLES:
            scope = 'company'

        result = []

        if scope == 'company':
            # Build executive layer first
            for exec_role in ['ceo', 'cfo', 'cto']:
                try:
                    exec_user = User.objects.get(role=exec_role, is_active=True)
                except User.DoesNotExist:
                    continue

                # Managers who report to this executive
                # Convention: managers whose department maps to this executive's domain
                # CEO sees all managers; CFO sees Finance/Accounting managers; CTO sees Tech managers
                if exec_role == 'ceo':
                    managers = User.objects.filter(
                        role='manager', is_active=True, manager=exec_user
                    ).order_by('department', 'first_name')
                    # Also include managers with no manager assigned as direct under CEO
                    unassigned_mgrs = User.objects.filter(
                        role='manager', is_active=True, manager__isnull=True
                    ).order_by('department', 'first_name')
                    managers = (managers | unassigned_mgrs).distinct().order_by('department', 'first_name')
                else:
                    managers = User.objects.filter(
                        role='manager', is_active=True, manager=exec_user
                    ).order_by('department', 'first_name')

                dept_blocks = []
                for mgr in managers:
                    employees = User.objects.filter(
                        manager=mgr, role='employee', is_active=True
                    ).order_by('first_name', 'last_name')

                    dept_blocks.append({
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

                result.append({
                    'executive': {
                        'id':        exec_user.id,
                        'full_name': f'{exec_user.first_name} {exec_user.last_name}'.strip(),
                        'email':     exec_user.email,
                        'role':      exec_role.upper(),
                    },
                    'departments': dept_blocks,
                })

        else:
            # Team scope — manager sees their own team; employee sees their manager's team
            if request.user.role == 'manager':
                mgr = request.user
            else:
                mgr = request.user.manager

            if mgr:
                employees = User.objects.filter(
                    manager=mgr, role='employee', is_active=True
                ).order_by('first_name', 'last_name')

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


# Frontend Page Views 

class LoginPageView(View):
    def get(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            try:
                AccessToken(raw_token)
                return redirect('dashboard')
            except TokenError:
                pass
        response = render(request, 'auth/login.html')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        return response


class DashboardView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'dashboard.html')


class ProfilePageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'profile.html')


class HierarchyPageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'hierarchy.html')


class AddToTeamPageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'add_to_team.html')