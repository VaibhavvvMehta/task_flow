from django.urls import path
from . import views

urlpatterns = [
    #Frontend pages 
    path('',views.LoginPageView.as_view(),name='login-page'),
    path('dashboard/',views.DashboardView.as_view(),name='dashboard'),
    path('profile/',views.ProfilePageView.as_view(),name='profile-page'),
    path('hierarchy/',views.HierarchyPageView.as_view(),name='hierarchy-page'), 
    

]

