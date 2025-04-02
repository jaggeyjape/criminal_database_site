from ..models import CriminalData
from django.shortcuts import get_object_or_404


def fetch_results(search_query):
    results = CriminalData.objects.filter(search_query)
    return list(results)

def fetch_unassigned(search_query):
    results = CriminalData.objects.filter(search_query)
    return results


def fetch_record(record_id):
    record = get_object_or_404(CriminalData, id=record_id)
    return record

def update_assigned_user(record_ids, username):
    if record_ids:
        updated_count = CriminalData.objects.filter(id__in=record_ids).update(assigned_to=username)
        print(f"✅ Assigned {updated_count} records to {username}")
    else:
        print(f"⚠️ No records to assign to {username}")
