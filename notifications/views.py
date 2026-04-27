"""
notifications/views.py
Notification API endpoints and page views.
"""

from django.shortcuts import render, redirect
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Notification


class NotificationListView(APIView):
    """GET /api/v1/notifications/ — list current user's notifications (newest first, max 50).
    Optional: ?unread=true  → only unread notifications.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user).select_related('task').order_by('-created_at')

        if request.query_params.get('unread') == 'true':
            qs = qs.filter(is_read=False)

        notifications = qs[:50]

        data = [{
            'id':         n.id,
            'type':       n.type,
            'title':      n.title,
            'message':    n.message,
            'is_read':    n.is_read,
            'created_at': n.created_at.isoformat(),
            'task_id':    n.task_id,
        } for n in notifications]

        return Response(data)


class NotificationMarkReadView(APIView):
    """PATCH /api/v1/notifications/<id>/read/ — mark a single notification as read."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, notif_id):
        try:
            notif = Notification.objects.get(id=notif_id, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)

        notif.is_read = True
        notif.save()
        return Response({'message': 'Marked as read.'})


class NotificationMarkAllReadView(APIView):
    """PATCH /api/v1/notifications/mark-all-read/ — mark all unread notifications as read."""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': f'{updated} notification(s) marked as read.'})


class NotificationUnreadCountView(APIView):
    """GET /api/v1/notifications/unread-count/ — used for the bell badge."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})


# Frontend View 

class NotificationsPageView(View):
    """Renders the notifications page — all roles."""
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'notifications.html')
