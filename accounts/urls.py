from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('token/refresh/',views.TokenRefreshView.as_view(),name='token_refresh'),
    path('me/',views.MeView.as_view(),name='me'),

    ##Frontend 
    path('',views.LoginPageView.as_view(),name='login'),
    path('dashboard/', views.DashboardView.as_view(),name='dashboard'),
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
]