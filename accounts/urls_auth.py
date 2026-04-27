from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('token/refresh/',views.TokenRefreshView.as_view(), name='token_refresh'),
    path('me/',views.MeView.as_view(),name='me'),
]
