from django.contrib import admin
from .models import Task, TaskStatusHistory, TaskAssignment, TaskComment
# Register your models here.

admin.site.register(Task)
admin.site.register(TaskStatusHistory)
admin.site.register(TaskAssignment)
admin.site.register(TaskComment)