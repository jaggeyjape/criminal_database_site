from django.shortcuts import render, redirect
from django.urls import path, reverse_lazy
from .views import user_login, results, search, user_logout, record_details


def home_redirect(request):
    return redirect("login")


LOGIN_REDIRECT_URL = reverse_lazy('search')
urlpatterns = [
    path("", home_redirect, name="home"),
    path("login/", user_login, name="login"),
    # path("search/",lambda request:render(request,"search.html"),name='search'),
    path("search/", search, name='search'),
    path("results/", results, name='results'),
    path("record/<uuid:record_id>", record_details, name='record_details'),
    path("logout/", user_logout, name='logout')
]
