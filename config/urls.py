from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend pages
    path('', include('accounts.urls')),        # login, dashboard
    path('', include('tasks.urls_frontend')),   # tasks pages

    # API
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/tasks/', include('tasks.urls')),
    path('api/v1/users/', include('accounts.urls')),

    # Dev
    path('__reload__/', include('django_browser_reload.urls')),
]