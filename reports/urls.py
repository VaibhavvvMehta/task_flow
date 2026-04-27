from django.urls import path
from . import views

urlpatterns = [
    path('my-performance/', views.MyPerformanceView.as_view(),  name='my-performance'),
    path('team-summary/',   views.TeamSummaryView.as_view(),    name='team-summary'),
    path('export/',         views.ExportView.as_view(),         name='report-export'),
]
