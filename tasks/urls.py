from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyTaskListView.as_view(), name='my-tasks'),
path('team-assign/', views.TeamAssignView.as_view(), name='team-assign'),
    path('manager/tasks/', views.ManagerOwnTasksView.as_view(), name='manager-own-tasks'),
    path('manager/team/tasks/', views.ManagerTeamView.as_view(), name='manager-team'),

    path('<int:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/status/', views.TaskStatusUpdateView.as_view(), name='task-status'),
    path('<int:task_id>/assign/', views.TaskReassignView.as_view(), name='task-reassign'),
]
