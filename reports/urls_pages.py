from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.ReportsPageView.as_view(), name='reports-page'),
]
