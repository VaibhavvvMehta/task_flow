from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationsPageView.as_view(), name='notifications-page'),
]
