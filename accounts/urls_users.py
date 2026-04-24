from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('hierarchy/', views.HierarchyView.as_view(),    name='hierarchy-data'),
]
