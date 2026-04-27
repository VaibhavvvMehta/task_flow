from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Task, TaskStatusHistory

User = get_user_model()


class AssignedUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'department']

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()


class TaskStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = TaskStatusHistory
        fields = ['id', 'old_status', 'new_status', 'changed_by_name', 'changed_at']

    def get_changed_by_name(self, obj):
        return f'{obj.changed_by.first_name} {obj.changed_by.last_name}'.strip()


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = AssignedUserSerializer(source='assigned_to', read_only=True)
    created_by_name    = serializers.SerializerMethodField()
    is_overdue         = serializers.SerializerMethodField()
    days_overdue       = serializers.SerializerMethodField()
    status_history     = TaskStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model  = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'assigned_to', 'assigned_to_detail',
            'created_by_name', 'is_overdue', 'days_overdue',
            'created_at', 'updated_at', 'status_history',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        return f'{obj.created_by.first_name} {obj.created_by.last_name}'.strip()

    def get_is_overdue(self, obj):
        if obj.due_date and obj.status != 'done' and not obj.is_deleted:
            return obj.due_date < timezone.now().date()
        return False

    def get_days_overdue(self, obj):
        if self.get_is_overdue(obj):
            return (timezone.now().date() - obj.due_date).days
        return 0


class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    due_date = serializers.DateField(required=True)

    class Meta:
        model  = Task
        fields = ['title', 'description', 'priority', 'due_date', 'assigned_to']

    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError('Title is required.')
        return value.strip()


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Task
        fields = ['title', 'description', 'priority', 'due_date']

    def validate_title(self, value):
        if value is not None and value.strip() == '':
            raise serializers.ValidationError('Title cannot be empty.')
        return value.strip() if value else value


class TaskStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['todo', 'in_progress', 'done'])