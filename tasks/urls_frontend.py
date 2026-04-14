from django.urls import path
from . import views_frontend

urlpatterns = [
    path('tasks/', views_frontend.MyTasksPageView.as_view(), name='my-tasks-page'),
    path('manager/tasks/', views_frontend.ManagerTasksPageView.as_view(), name='manager-tasks-page'),
    path('manager/team/', views_frontend.TeamViewPageView.as_view(), name='team-view-page'),
    path('manager/assign/', views_frontend.AssignTaskPageView.as_view(), name='assign-task-page'),
]