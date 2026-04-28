from django.urls import path
from . import views

urlpatterns = [
    # Fetching data for frontend views
    path('employees/',  views.EmployeeListView.as_view(), name='employee-list'),
    path('hierarchy/',  views.HierarchyView.as_view(),    name='hierarchy-data'),
    path('team/add/',   views.AddToTeamView.as_view(),    name='add-to-team'),
]