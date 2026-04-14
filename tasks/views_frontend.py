from django.shortcuts import render, redirect
from django.views import View

class MyTasksPageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'my_tasks.html')

class ManagerTasksPageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'manager_task.html')

class TeamViewPageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'team_view.html')

class AssignTaskPageView(View):
    def get(self, request):
        if not request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'assign_task.html')