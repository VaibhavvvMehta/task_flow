from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Task, TaskStatusHistory, TaskAssignment
from .serializers import (
    TaskSerializer, TaskCreateSerializer,
    TaskUpdateSerializer, TaskStatusUpdateSerializer,
)
from notifications.utils import notify

# Create your views here.

User = get_user_model()


def get_active_task(task_id):
    try:
        return Task.objects.get(id=task_id, is_deleted=False)
    except Task.DoesNotExist:
        return None


# ── My Tasks — all roles see their own assigned tasks ─────────────────────────

class MyTaskListView(APIView):
    """
    GET /api/v1/tasks/
    Returns tasks assigned to logged-in user.
    Supports ?status= ?priority= ?search=
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(
            assigned_to=request.user,
            is_deleted=False,
        ).select_related('assigned_to', 'created_by').prefetch_related('status_history').order_by('-created_at')

        status_filter   = request.query_params.get('status', '').strip()
        priority_filter = request.query_params.get('priority', '').strip()
        search          = request.query_params.get('search', '').strip()

        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        if search:
            tasks = tasks.filter(title__icontains=search)

        return Response(TaskSerializer(tasks, many=True).data)


# ── Task Detail / Edit / Soft Delete ─────────────────────────────────────────

class TaskDetailView(APIView):
    """
    GET    /api/v1/tasks/<id>/  — employee sees own only; manager/admin sees any
    PATCH  /api/v1/tasks/<id>/  — manager/admin only
    DELETE /api/v1/tasks/<id>/  — manager/admin only (soft delete)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_active_task(task_id)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'employee' and task.assigned_to != request.user:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(TaskSerializer(task).data)

    def patch(self, request, task_id):
        if request.user.role not in ['manager', 'admin']:
            return Response(
                {'error': 'Only managers and admins can edit tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        task = get_active_task(task_id)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            task.refresh_from_db()
            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        if request.user.role not in ['manager', 'admin']:
            return Response(
                {'error': 'Only managers and admins can delete tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        task = get_active_task(task_id)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        task.is_deleted = True
        task.save()
        return Response({'message': 'Task deleted successfully.'})


# ── Create Task (single assign) ───────────────────────────────────────────────

class TaskCreateView(APIView):
    """POST /api/v1/tasks/create/ — manager/admin assigns to one employee"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['manager', 'admin']:
            return Response(
                {'error': 'Only managers and admins can create tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task = serializer.save(created_by=request.user)

        TaskAssignment.objects.create(
            task=task,
            assigned_to=task.assigned_to,
            assigned_by=request.user,
        )

        notify(
            user=task.assigned_to,
            notif_type='task_assigned',
            title='New Task Assigned',
            message=f'You have been assigned "{task.title}" by {request.user.first_name} {request.user.last_name}.'.strip(),
            task=task,
        )

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


# ── Team Assign ───────────────────────────────────────────────────────────────

class TeamAssignView(APIView):
    """
    POST /api/v1/tasks/team-assign/
    Creates one Task record per employee in the list.
    Body: { title, description, priority, due_date, assigned_to: [id1, id2, ...] }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['manager', 'admin']:
            return Response(
                {'error': 'Only managers and admins can assign tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_ids = request.data.get('assigned_to', [])
        if not isinstance(user_ids, list) or len(user_ids) == 0:
            return Response(
                {'error': 'assigned_to must be a non-empty list of user IDs.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_tasks = []
        errors        = []

        for user_id in user_ids:
            data       = {**request.data, 'assigned_to': user_id}
            serializer = TaskCreateSerializer(data=data)
            if serializer.is_valid():
                task = serializer.save(created_by=request.user)
                TaskAssignment.objects.create(
                    task=task,
                    assigned_to=task.assigned_to,
                    assigned_by=request.user,
                )
                notify(
                    user=task.assigned_to,
                    notif_type='task_assigned',
                    title='New Task Assigned',
                    message=f'You have been assigned "{task.title}" by {request.user.first_name} {request.user.last_name}.'.strip(),
                    task=task,
                )
                created_tasks.append(TaskSerializer(task).data)
            else:
                errors.append({'user_id': user_id, 'errors': serializer.errors})

        return Response({
            'created': len(created_tasks),
            'tasks':   created_tasks,
            'errors':  errors,
        }, status=status.HTTP_201_CREATED)


# ── Status Update ─────────────────────────────────────────────────────────────

class TaskStatusUpdateView(APIView):
    """
    PATCH /api/v1/tasks/<id>/status/
    Employee updates own task only.
    Manager/Admin can update any task.
    Every change logged to TaskStatusHistory.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        task = get_active_task(task_id)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'employee' and task.assigned_to != request.user:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']
        old_status = task.status

        if old_status == new_status:
            return Response({'message': 'Status unchanged.'})

        TaskStatusHistory.objects.create(
            task=task,
            changed_by=request.user,
            old_status=old_status,
            new_status=new_status,
        )

        task.status = new_status
        if new_status == 'done':
            task.done_at = timezone.now()
        elif old_status == 'done':
            # Task moved back out of done — clear the timestamp
            task.done_at = None
        task.save(update_fields=['status', 'done_at', 'updated_at'])

        STATUS_LABELS = {'todo': 'To Do', 'in_progress': 'In Progress', 'done': 'Done'}
        old_label = STATUS_LABELS.get(old_status, old_status)
        new_label = STATUS_LABELS.get(new_status, new_status)

        # Employee updates → notify the task creator (manager)
        if request.user.role == 'employee' and task.created_by and task.created_by != request.user:
            notify(
                user=task.created_by,
                notif_type='task_status_changed',
                title='Task Status Updated',
                message=f'{request.user.first_name} {request.user.last_name} changed "{task.title}" from {old_label} to {new_label}.'.strip(),
                task=task,
            )
        # Manager/admin updates → notify the assigned employee
        elif request.user.role in ['manager', 'admin'] and task.assigned_to != request.user:
            notify(
                user=task.assigned_to,
                notif_type='task_status_changed',
                title='Task Status Updated',
                message=f'Your task "{task.title}" was changed from {old_label} to {new_label} by {request.user.first_name} {request.user.last_name}.'.strip(),
                task=task,
            )

        return Response({
            'message': f'Status updated: {old_status} → {new_status}',
            'task':    TaskSerializer(task).data,
        })


# ── Reassign ──────────────────────────────────────────────────────────────────

class TaskReassignView(APIView):
    """PATCH /api/v1/tasks/<id>/assign/ — manager/admin reassigns to different employee"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        if request.user.role not in ['manager', 'admin']:
            return Response(
                {'error': 'Only managers and admins can reassign tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        task = get_active_task(task_id)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_user_id = request.data.get('assigned_to')
        if not new_user_id:
            return Response({'error': 'assigned_to is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_user = User.objects.get(id=new_user_id, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'User not found or inactive.'}, status=status.HTTP_404_NOT_FOUND)

        task.assigned_to = new_user
        task.save()

        TaskAssignment.objects.create(
            task=task,
            assigned_to=new_user,
            assigned_by=request.user,
        )

        notify(
            user=new_user,
            notif_type='task_assigned',
            title='Task Reassigned to You',
            message=f'You have been assigned "{task.title}" by {request.user.first_name} {request.user.last_name}.'.strip(),
            task=task,
        )

        return Response({
            'message': f'Task reassigned to {new_user.first_name} {new_user.last_name}'.strip(),
            'task':    TaskSerializer(task).data,
        })


# ── Manager: Own Tasks ────────────────────────────────────────────────────────

class ManagerOwnTasksView(APIView):
    """
    GET /api/v1/manager/my-tasks/
    Tasks assigned TO the manager themselves.
    Supports ?status= ?priority=
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['manager', 'admin']:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        tasks = Task.objects.filter(
            assigned_to=request.user,
            is_deleted=False,
        ).select_related('assigned_to', 'created_by').prefetch_related('status_history').order_by('-created_at')

        status_filter   = request.query_params.get('status', '').strip()
        priority_filter = request.query_params.get('priority', '').strip()

        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)

        return Response(TaskSerializer(tasks, many=True).data)


# ── Manager: Team View ────────────────────────────────────────────────────────

class ManagerTeamView(APIView):
    """
    GET /api/v1/manager/team/
    Employees in the same department as the manager,
    each with their task counts and full task list.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['manager', 'admin']:
            return Response({'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()

        # Single query: annotate all counts directly on the employee queryset
        employees = User.objects.filter(
            manager=request.user,
            role='employee',
            is_active=True,
        ).annotate(
            total_tasks=Count(
                'assigned_tasks',
                filter=Q(assigned_tasks__is_deleted=False),
            ),
            todo_count=Count(
                'assigned_tasks',
                filter=Q(assigned_tasks__is_deleted=False, assigned_tasks__status='todo'),
            ),
            in_progress_count=Count(
                'assigned_tasks',
                filter=Q(assigned_tasks__is_deleted=False, assigned_tasks__status='in_progress'),
            ),
            done_count=Count(
                'assigned_tasks',
                filter=Q(assigned_tasks__is_deleted=False, assigned_tasks__status='done'),
            ),
            overdue_count=Count(
                'assigned_tasks',
                filter=Q(
                    assigned_tasks__is_deleted=False,
                    assigned_tasks__status__in=['todo', 'in_progress'],
                    assigned_tasks__due_date__lt=today,
                ),
            ),
        )

        result = []
        for emp in employees:
            tasks = Task.objects.filter(
                assigned_to=emp, is_deleted=False
            ).select_related('assigned_to', 'created_by').prefetch_related('status_history').order_by('-created_at')

            result.append({
                'id':         emp.id,
                'full_name':  f'{emp.first_name} {emp.last_name}'.strip(),
                'email':      emp.email,
                'department': emp.department,
                'task_counts': {
                    'total':       emp.total_tasks,
                    'todo':        emp.todo_count,
                    'in_progress': emp.in_progress_count,
                    'done':        emp.done_count,
                    'overdue':     emp.overdue_count,
                },
                'tasks': TaskSerializer(tasks, many=True).data,
            })

        return Response(result)