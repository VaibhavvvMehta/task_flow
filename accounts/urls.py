from django.urls import path
from . import views

urlpatterns = [
    # ── Frontend pages ────────────────────────────────────────
    path('',           views.LoginPageView.as_view(),     name='login-page'),
    path('dashboard/', views.DashboardView.as_view(),     name='dashboard'),
    path('hierarchy/', views.HierarchyPageView.as_view(), name='hierarchy-page'),
]
