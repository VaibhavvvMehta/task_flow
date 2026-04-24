from django.urls import path
from . import views

urlpatterns = [
    path('my-performance/', views.MyPerformanceView.as_view(), name='my-performance'),
]