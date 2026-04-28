from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', views.NotificationUnreadCountView.as_view(), name='notif-unread-count'),
    path('mark-all-read/', views.NotificationMarkAllReadView.as_view(), name='notif-mark-all-read'),
    path('<int:notif_id>/read/', views.NotificationMarkReadView.as_view(), name='notif-mark-read'),
]
