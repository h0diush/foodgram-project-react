from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadAnllyUser(BasePermission):
    def has_permission(self, request, view):
        if request.method == SAFE_METHODS[0]:
            return True
        if (request.user.is_authenticated
            and request.user.is_superuser == True
                and request.user.is_staff == True):
            return True
        return False


class IsAuthorRecipeOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        return request.user == obj.author
