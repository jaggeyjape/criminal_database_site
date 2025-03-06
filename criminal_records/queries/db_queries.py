from ..models import CriminalData
from django.shortcuts import get_object_or_404


def fetch_results(search_query):
    results = CriminalData.objects.filter(search_query)
    return list(results)


def fetch_record(record_id):
    record = get_object_or_404(CriminalData, id=record_id)
    return record
