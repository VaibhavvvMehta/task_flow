"""
notifications/utils.py
Helper for creating Notification records from anywhere in the app.
"""

from .models import Notification


def notify(user, notif_type, title, message, task=None):
    """Create a notification for a user. Silently no-ops on error."""
    try:
        Notification.objects.create(
            user=user,
            type=notif_type,
            title=title,
            message=message,
            task=task,
        )
    except Exception:
        pass
