from django.db import models
from django.conf import settings
# Create your models here.
class SystemSetting(models.Model):
    key         = models.CharField(max_length=100, unique=True)
    value       = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.key} = {self.value}'