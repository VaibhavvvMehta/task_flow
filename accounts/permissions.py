from rest_framework.permissions import BasePermission

# ----**When each permission is used:**---
# IsEmployee       → My Tasks, My Performance, Task History
# IsManager        → Assign Task, Team Overview, Manager Dashboard
# IsAdmin          → User Management, Admin Panel
# IsManagerOrAdmin → Create task, Edit task, Delete task, CSV export
# IsManagerOrEmployee → Update task status, Add comment, View notifications

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsManagerOrEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['manager', 'employee']


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['manager', 'admin']


