from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("/accounts/login")
        return function(request, *args, **kwargs)

    return _inner
