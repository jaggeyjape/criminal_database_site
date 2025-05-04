from django.shortcuts import redirect
from urllib.parse import urlencode


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_logged_in", False):
            return redirect("login")
        if "authorized" not in request.GET:
            # Preserve all existing GET params and add `authorized=true`
            params = request.GET.copy()
            params["authorized"] = "true"
            return redirect(f"{request.path}?{urlencode(params)}")
        # Redirect to login page
        return view_func(request, *args, **kwargs)

    return wrapper

