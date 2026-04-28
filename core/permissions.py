from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)

class IsRoleUser(permissions.BasePermission):
    """Base class to check specific roles."""
    allowed_roles = []
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.role in self.allowed_roles or request.user.is_superuser)

class IsAdminOrHR(IsRoleUser):
    allowed_roles = ['admin', 'hr']

class IsAdminOrAccountant(IsRoleUser):
    allowed_roles = ['admin', 'accountant']

class IsAdminOrFaculty(IsRoleUser):
    allowed_roles = ['admin', 'faculty']

class IsAdminOrLibrarian(IsRoleUser):
    allowed_roles = ['admin', 'librarian']
