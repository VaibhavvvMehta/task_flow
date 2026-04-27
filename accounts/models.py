from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


EXECUTIVE_ROLES = ['ceo', 'cfo', 'cto']
ELEVATED_ROLES  = ['manager', 'ceo', 'cfo', 'cto']


class User(AbstractUser):

    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager',  'Manager'),
        ('ceo',      'CEO'),
        ('cfo',      'CFO'),
        ('cto',      'CTO'),
    ]

    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True, null=True)
    manager    = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='direct_reports',
    )

    def __str__(self):
        return f'{self.username} ({self.role})'