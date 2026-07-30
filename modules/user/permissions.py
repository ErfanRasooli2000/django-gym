from rest_framework import permissions


class CanCRUDUser(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user

        if user.has_perm("user.view_user"):
            print(user.username)
            return True

        return False