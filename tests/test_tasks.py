import pytest
from django.utils import timezone
from datetime import date, timedelta
from rest_framework import status
from tasks.models import Task, TaskStatusHistory, TaskAssignment

pytestmark = pytest.mark.django_db


class TestTaskCreate:
    """Test task creation by different roles."""

    def test_manager_can_create_task(self, manager_api_client, employee_user):
        """Manager can create a task."""
        response = manager_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 'high',
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'assigned_to': [employee_user.id],
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 1
        assert response.data['tasks'][0]['title'] == 'Test Task'

    def test_ceo_can_create_task(self, ceo_api_client, employee_user):
        """CEO can create a task for any employee."""
        response = ceo_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'CEO Task',
            'description': 'From CEO',
            'priority': 'high',
            'due_date': (date.today() + timedelta(days=3)).isoformat(),
            'assigned_to': [employee_user.id],
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 1

    def test_cto_can_create_task(self, cto_api_client, employee_user):
        """CTO can create a task."""
        response = cto_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'CTO Task',
            'description': 'From CTO',
            'priority': 'medium',
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
            'assigned_to': [employee_user.id],
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_cfo_can_create_task(self, cfo_api_client, employee_user):
        """CFO can create a task."""
        response = cfo_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'CFO Task',
            'description': 'Finance task',
            'priority': 'high',
            'due_date': (date.today() + timedelta(days=2)).isoformat(),
            'assigned_to': [employee_user.id],
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_employee_cannot_create_task(self, authenticated_api_client, employee_user_2):
        """Employees cannot create tasks."""
        response = authenticated_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'Unauthorized Task',
            'description': 'Should fail',
            'priority': 'high',
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'assigned_to': [employee_user_2.id],
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_task_requires_assigned_to_list(self, manager_api_client):
        """Task creation requires assigned_to list."""
        response = manager_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'Task',
            'description': 'No assigned_to',
            'priority': 'high',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_task_with_multiple_employees(self, manager_api_client, employee_user, employee_user_2):
        """Manager can assign same task to multiple employees."""
        response = manager_api_client.post('/api/v1/tasks/team-assign/', {
            'title': 'Team Task',
            'description': 'For multiple people',
            'priority': 'medium',
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'assigned_to': [employee_user.id, employee_user_2.id],
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 2


class TestTaskRead:
    """Test task retrieval."""

    def test_employee_can_see_own_tasks(self, authenticated_api_client):
        """Employee can retrieve their own tasks."""
        # Create a task first
        task = Task.objects.create(
            title='My Task',
            description='Task for employee',
            priority='high',
            status='todo',
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        response = authenticated_api_client.get('/api/v1/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(t['id'] == task.id for t in response.data)

    def test_employee_cannot_see_others_tasks(self, authenticated_api_client, employee_user_2, manager_user):
        """Employee cannot see another employee's tasks."""
        task = Task.objects.create(
            title='Other Task',
            description='For another employee',
            priority='high',
            status='todo',
            assigned_to=employee_user_2,
            created_by=manager_user,
        )
        response = authenticated_api_client.get('/api/v1/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert not any(t['id'] == task.id for t in response.data)

    def test_manager_can_view_team_tasks(self, manager_api_client, employee_user, employee_user_2):
        """Manager can view all their team's tasks."""
        task1 = Task.objects.create(
            title='Task 1',
            assigned_to=employee_user,
            created_by=manager_api_client.user,
            priority='high',
        )
        task2 = Task.objects.create(
            title='Task 2',
            assigned_to=employee_user_2,
            created_by=manager_api_client.user,
            priority='high',
        )
        response = manager_api_client.get('/api/v1/tasks/manager/team/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_get_task_detail_by_id(self, authenticated_api_client):
        """Can retrieve a task by ID."""
        task = Task.objects.create(
            title='Detail Task',
            description='Test detail',
            priority='high',
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        response = authenticated_api_client.get(f'/api/v1/tasks/{task.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == task.id
        assert response.data['title'] == 'Detail Task'

    def test_task_detail_not_found(self, authenticated_api_client):
        """Requesting non-existent task returns 404."""
        response = authenticated_api_client.get('/api/v1/tasks/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskUpdate:
    """Test task updates."""

    def test_manager_can_edit_task(self, manager_api_client, employee_user):
        """Manager can edit a task."""
        task = Task.objects.create(
            title='Original Title',
            priority='low',
            assigned_to=employee_user,
            created_by=manager_api_client.user,
        )
        response = manager_api_client.patch(f'/api/v1/tasks/{task.id}/', {
            'title': 'Updated Title',
            'priority': 'high',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
        assert response.data['priority'] == 'high'

    def test_employee_cannot_edit_task(self, authenticated_api_client, manager_user):
        """Employee cannot edit tasks (only their own status)."""
        task = Task.objects.create(
            title='Task',
            priority='high',
            assigned_to=authenticated_api_client.user,
            created_by=manager_user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/', {
            'title': 'Hacked Title',
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_employee_cannot_edit_others_task(self, authenticated_api_client, employee_user_2, manager_user):
        """Employee cannot edit another employee's task."""
        task = Task.objects.create(
            title='Other Task',
            assigned_to=employee_user_2,
            created_by=manager_user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/', {
            'title': 'Hacked',
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_ceo_can_edit_any_task(self, ceo_api_client, employee_user, manager_user):
        """CEO can edit any task."""
        task = Task.objects.create(
            title='Task',
            assigned_to=employee_user,
            created_by=manager_user,
        )
        response = ceo_api_client.patch(f'/api/v1/tasks/{task.id}/', {
            'title': 'CEO Updated',
        })
        assert response.status_code == status.HTTP_200_OK


class TestTaskDelete:
    """Test task deletion (soft delete)."""

    def test_manager_can_delete_task(self, manager_api_client, employee_user):
        """Manager can delete a task (soft delete)."""
        task = Task.objects.create(
            title='Task to Delete',
            assigned_to=employee_user,
            created_by=manager_api_client.user,
        )
        assert task.is_deleted is False
        
        response = manager_api_client.delete(f'/api/v1/tasks/{task.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        task.refresh_from_db()
        assert task.is_deleted is True

    def test_employee_cannot_delete_task(self, authenticated_api_client, manager_user):
        """Employee cannot delete tasks."""
        task = Task.objects.create(
            title='Task',
            assigned_to=authenticated_api_client.user,
            created_by=manager_user,
        )
        response = authenticated_api_client.delete(f'/api/v1/tasks/{task.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_deleted_task_not_visible(self, authenticated_api_client):
        """Deleted tasks don't appear in task lists."""
        task = Task.objects.create(
            title='Deleted Task',
            is_deleted=True,
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        response = authenticated_api_client.get('/api/v1/tasks/')
        assert not any(t['id'] == task.id for t in response.data)


class TestTaskStatusUpdate:
    """Test task status transitions."""

    def test_employee_can_update_own_task_status(self, authenticated_api_client):
        """Employee can change their own task status."""
        task = Task.objects.create(
            title='Task',
            status='todo',
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/status/', {
            'status': 'in_progress',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['task']['status'] == 'in_progress'

    def test_employee_can_mark_done(self, authenticated_api_client):
        """Employee can mark task as done."""
        task = Task.objects.create(
            title='Task',
            status='in_progress',
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/status/', {
            'status': 'done',
        })
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.done_at is not None

    def test_employee_cannot_change_others_status(self, authenticated_api_client, employee_user_2, manager_user):
        """Employee cannot change another employee's task status."""
        task = Task.objects.create(
            title='Other Task',
            status='todo',
            assigned_to=employee_user_2,
            created_by=manager_user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/status/', {
            'status': 'done',
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_manager_can_update_any_status(self, manager_api_client, employee_user):
        """Manager can update any team member's task status."""
        task = Task.objects.create(
            title='Task',
            status='todo',
            assigned_to=employee_user,
            created_by=manager_api_client.user,
        )
        response = manager_api_client.patch(f'/api/v1/tasks/{task.id}/status/', {
            'status': 'done',
        })
        assert response.status_code == status.HTTP_200_OK

    def test_status_change_creates_history(self, authenticated_api_client):
        """Task status changes are recorded in history."""
        task = Task.objects.create(
            title='Task',
            status='todo',
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/status/', {
            'status': 'in_progress',
        })
        
        history = TaskStatusHistory.objects.filter(task=task)
        assert history.exists()
        assert history.first().old_status == 'todo'
        assert history.first().new_status == 'in_progress'

    def test_invalid_status_rejected(self, authenticated_api_client):
        """Invalid status values are rejected."""
        task = Task.objects.create(
            title='Task',
            assigned_to=authenticated_api_client.user,
            created_by=authenticated_api_client.user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/status/', {
            'status': 'invalid_status',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTaskReassign:
    """Test task reassignment."""

    def test_manager_can_reassign_task(self, manager_api_client, employee_user, employee_user_2):
        """Manager can reassign task to different employee."""
        task = Task.objects.create(
            title='Task',
            assigned_to=employee_user,
            created_by=manager_api_client.user,
        )
        response = manager_api_client.patch(f'/api/v1/tasks/{task.id}/assign/', {
            'assigned_to': employee_user_2.id,
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['task']['assigned_to_detail']['id'] == employee_user_2.id

    def test_employee_cannot_reassign_task(self, authenticated_api_client, employee_user_2, manager_user):
        """Employee cannot reassign tasks."""
        task = Task.objects.create(
            title='Task',
            assigned_to=authenticated_api_client.user,
            created_by=manager_user,
        )
        response = authenticated_api_client.patch(f'/api/v1/tasks/{task.id}/assign/', {
            'assigned_to': employee_user_2.id,
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reassignment_creates_assignment_record(self, manager_api_client, employee_user, employee_user_2):
        """Reassignment creates TaskAssignment record."""
        task = Task.objects.create(
            title='Task',
            assigned_to=employee_user,
            created_by=manager_api_client.user,
        )
        manager_api_client.patch(f'/api/v1/tasks/{task.id}/assign/', {
            'assigned_to': employee_user_2.id,
        })
        
        assignment = TaskAssignment.objects.filter(task=task, assigned_to=employee_user_2).first()
        assert assignment is not None
        assert assignment.assigned_by == manager_api_client.user