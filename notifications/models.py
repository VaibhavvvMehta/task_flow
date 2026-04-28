from django.db import models
from django.conf import settings
# Create your models here.

class Notification(models.Model):

    TYPE_CHOICES = [
        ('task_assigned','Task Assigned'),
        ('task_overdue','Task Overdue'),
        ('task_due_reminder','Task Due Reminder'),
        ('task_status_changed','Task Status Changed'),
        ('task_comment_added','Task Comment Added'),
    ]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type       = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    task       = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, blank=True, null=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type} for {self.user}'
