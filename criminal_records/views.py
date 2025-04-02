# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.http import HttpResponseRedirect
# from django.core.paginator import Paginator
# from django.db.models import Q
# from .queries.db_queries import fetch_results, fetch_record
# from .decorators import login_required
#
#
# def user_login(request):
#     if request.session.get("is_logged_in"):
#         return HttpResponseRedirect(reverse("search") + "?authorized=true")
#     if request.method == "POST":
#         user = request.POST.get("username")
#         password = request.POST.get("password")
#         if user == 'bodycamteam' and password == 'f13bodycamteam':
#             request.session["is_logged_in"] = True
#             return HttpResponseRedirect(reverse("search") + "?authorized=true")
#         else:
#             return HttpResponseRedirect(reverse("login") + "?denied")
#
#     return render(request, 'criminal_records/login.html')
#
#
# @login_required
# def search(request):
#     return render(request, 'criminal_records/search.html')
#
#
# def results(request):
#     queries = []
#     exact_match = request.GET.get('exact_match')
#     search_fields = ['name', 'age', 'crime_title', 'charge_description']
#     for field in search_fields:
#         value = request.GET.get(field, '').strip()
#         if value:
#             queries.append(Q(**{f"{field}__icontains": value}))
#     p_obj = None
#     if queries:
#         filters = Q()
#         for query in queries:
#             if exact_match == 'on':
#                 filters &= query
#             else:
#                 filters |= query
#         records = fetch_results(filters)
#         paginator = Paginator(records, 50)
#         p_no = request.GET.get('page')
#         p_obj = paginator.get_page(p_no)
#     return render(request, 'criminal_records/result.html', {
#         'request': request,
#         'page_obj': p_obj,
#     })
#
#
# def record_details(request, record_id):
#     record = fetch_record(record_id)
#     record_dict = {k: v for k, v in vars(record).items() if not k.startswith('_')}  # Remove private attributes
#     return render(request, 'criminal_records/record_details.html', {'record': record_dict})
#
#
# def user_logout(request):
#     request.session.flush()
#     return redirect("login")
#
#

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

from .models import CriminalData
from .queries.db_queries import fetch_results, fetch_record, update_assigned_user,fetch_unassigned
from .decorators import login_required
import boto3
from django.http import HttpResponse
from django.conf import settings

# Define static users
STATIC_USERS = ["user1", "user2", "user3"]



def get_s3_image(request, record_id):
    # Get the record from the database
    record = CriminalData.objects.get(id=record_id)
    s3_url = record.image  # Get the S3 URL from the database

    # Parse the bucket and key from the URL
    bucket_name = 'bodycam-mugshots'  # Your bucket name
    key = s3_url.replace(f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/", "")

    # Initialize S3 client
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME)

    try:
        # Fetch the image from S3
        s3_response = s3.get_object(Bucket=bucket_name, Key=key)
        file_content = s3_response['Body'].read()

        # Return the image response
        return HttpResponse(file_content, content_type='image/jpeg')
    except s3.exceptions.NoSuchKey:
        return HttpResponse("Image not found", status=404)


def get_current_week_date_range():
    """Get start and end of the current week as naive dates."""
    today = datetime.today().date()
    start_date = today - timedelta(days=today.weekday())
    start_date = start_date - timedelta(days=1)# Monday
    end_date = start_date + timedelta(days=6)  # Sunday
    return start_date, end_date


def assign_weekly_records():
    """Assign unassigned records equally to static users for the current week."""
    start_date, end_date = get_current_week_date_range()
    print(start_date, end_date)

    records = fetch_unassigned(Q(created_at__range=(start_date, end_date), assigned_to__isnull=True))
    if not records:
        print("No records to assign.")
        return

    total_records = records
    print(f"Total unassigned records: {total_records}")
    total_records = len(records)
    if total_records == 0:
        return  # No records to assign

    # Divide records among users
    chunk_size = total_records // 3
    remainder = total_records % 3

    user_chunks = [
        records[:chunk_size],
        records[chunk_size:chunk_size * 2],
        records[chunk_size * 2:],
    ]

    # Distribute the remainder to the last user
    if remainder > 0:
        user_chunks[2] += records[len(records) - remainder:]

    # Assign records
    for i, user in enumerate(STATIC_USERS):
        record_ids = [record.id for record in user_chunks[i]]
        if record_ids:
            update_assigned_user(record_ids, user)  # Update database with assigned user

@csrf_exempt
def user_login(request):
    """Handle user login and trigger record assignment if needed."""
    if request.session.get("is_logged_in"):
        return HttpResponseRedirect(reverse("search") + "?authorized=true")

    if request.method == "POST":
        user = request.POST.get("username")
        password = request.POST.get("password")

        # Static user credentials
        static_credentials = {
            "user1": "password1",
            "user2": "password2",
            "user3": "password3",
            "bodycamteam": "f13bodycamteam",
        }

        if user in static_credentials and password == static_credentials[user]:
            # Set session variables
            request.session["is_logged_in"] = True
            request.session["username"] = user

            # Assign weekly records on first login of the week
            assign_weekly_records()

            return HttpResponseRedirect(reverse("search") + "?authorized=true")
        else:
            return HttpResponseRedirect(reverse("login") + "?denied")

    return render(request, 'criminal_records/login.html')


@login_required
def search(request):
    """Render search page."""
    username = request.session.get("username")
    return render(request, 'criminal_records/search.html', {'username': username})

def results(request):
    queries = []
    exact_match = request.GET.get('exact_match')
    search_fields = ['c_id','name', 'age', 'crime_title', 'charge_description']
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

@login_required
def assigned(request):
    p_obj = None
    username = request.session.get("username")
    filters = Q(assigned_to=username)
    # Fetch records assigned to the current user
    records = fetch_results(filters)
    paginator = Paginator(records, 50)
    p_no = request.GET.get('page')
    p_obj = paginator.get_page(p_no)


    return render(request, 'criminal_records/assigned.html', {
        'request': request,
        'page_obj': p_obj,
    })


@login_required
def record_details(request, record_id):
    """Display detailed view of a single record."""
    record = fetch_record(record_id)
    record_dict = {k: v for k, v in vars(record).items() if not k.startswith('_')}
    return render(request, 'criminal_records/record_details.html', {'record': record_dict})


def user_logout(request):
    """Clear session and log out user."""
    request.session.flush()
    return redirect("login")
