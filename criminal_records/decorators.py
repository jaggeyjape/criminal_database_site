from django.shortcuts import redirect


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_logged_in", False):
            return redirect("login")
        if "authorized" not in request.GET:
            return redirect(request.path + "?authorized=true")# Redirect to login page
        return view_func(request, *args, **kwargs)

    return wrapper

