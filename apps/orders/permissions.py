from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == "STAFF"
    
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated  and request.user.is_email_verified
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
    
class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "STAFF"
    
class IsOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_email_verified

    def has_object_permission(self, request, view, obj):
        if request.user.role == "STAFF":
            return True
        if hasattr(obj,'user'):
            return obj.user == request.user
        elif hasattr(obj,'cart'):
            return obj.cart.user == request.user
        return False