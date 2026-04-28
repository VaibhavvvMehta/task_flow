from django.urls import path
from . import views

urlpatterns = [
    path('tasks/',          views.MyTasksPageView.as_view(),      name='my-tasks-page'),
    path('manager/tasks/',  views.ManagerTasksPageView.as_view(), name='manager-tasks-page'),
    path('manager/team/',   views.TeamViewPageView.as_view(),     name='team-view-page'),
    path('manager/assign/', views.AssignTaskPageView.as_view(),   name='assign-task-page'),
]
