from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q
from .queries.db_queries import fetch_results, fetch_record
from .decorators import login_required


def user_login(request):
    if request.session.get("is_logged_in"):
        return HttpResponseRedirect(reverse("search") + "?authorized=true")
    if request.method == "POST":
        user = request.POST.get("username")
        password = request.POST.get("password")
        if user == 'bodycamteam' and password == 'f13bodycamteam':
            request.session["is_logged_in"] = True
            return HttpResponseRedirect(reverse("search") + "?authorized=true")
        else:
            return HttpResponseRedirect(reverse("login") + "?denied")

    return render(request, 'criminal_records/login.html')


@login_required
def search(request):
    return render(request, 'criminal_records/search.html')


def results(request):
    queries = []
    exact_match = request.GET.get('exact_match')
    search_fields = ['name', 'age', 'crime_title', 'charge_description']
    for field in search_fields:
        value = request.GET.get(field, '').strip()
        if value:
            queries.append(Q(**{f"{field}__icontains": value}))
    p_obj = None
    if queries:
        filters = Q()
        for query in queries:
            if exact_match == 'on':
                filters &= query
            else:
                filters |= query
        records = fetch_results(filters)
        paginator = Paginator(records, 50)
        p_no = request.GET.get('page')
        p_obj = paginator.get_page(p_no)
    return render(request, 'criminal_records/result.html', {
        'request': request,
        'page_obj': p_obj,
    })


def record_details(request, record_id):
    record = fetch_record(record_id)
    record_dict = {k: v for k, v in vars(record).items() if not k.startswith('_')}  # Remove private attributes
    return render(request, 'criminal_records/record_details.html', {'record': record_dict})


def user_logout(request):
    request.session.flush()
    return redirect("login")
