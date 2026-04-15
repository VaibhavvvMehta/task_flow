from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Frontend pages ────────────────────────────────────────
    path('', include('accounts.urls')),       # login, dashboard, notifications, hierarchy
    path('', include('tasks.urls_frontend')), # tasks pages

    # ── REST API ──────────────────────────────────────────────
    path('api/v1/auth/',include('accounts.urls_auth')),
    path('api/v1/users/',include('accounts.urls_users')),
    path('api/v1/tasks/',include('tasks.urls')),
    path('api/v1/notifications/',include('notifications.urls')),
    path('api/v1/reports/', include('reports.urls')),

    # ── Dev ───────────────────────────────────────────────────
    path('__reload__/', include('django_browser_reload.urls')),
]
