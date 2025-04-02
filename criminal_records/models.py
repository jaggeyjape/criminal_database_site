from django.db import models
from datetime import datetime


class CriminalData(models.Model):
    id = models.UUIDField(primary_key=True, db_column='ID')
    c_id = models.IntegerField(db_column='C_ID', null=False,default=0)
    source_site = models.TextField(db_column='Source Site', null=False)
    crime_title = models.TextField(db_column='Crime Title', null=True)
    charge_description = models.TextField(db_column='Charge Description', null=True)
    police_department = models.TextField(db_column='Police Department', null=True)
    name = models.TextField(db_column='Name', null=True)
    age = models.TextField(db_column='Age', null=True)
    dob = models.TextField(db_column='Date Of Birth', null=True)
    gender = models.TextField(db_column='Gender', null=True)
    race = models.TextField(db_column='Race', null=True)
    height = models.TextField(db_column='Height', null=True)
    weight = models.TextField(db_column='Weight', null=True)
    city = models.TextField(db_column='City', null=True)
    address = models.TextField(db_column='Address', null=True)
    arrest_date = models.TextField(db_column='Arrest Date', null=True)
    release_date = models.TextField(db_column='Release Date', null=True)
    prisoner_type = models.TextField(db_column='Prisoner Type', null=True)
    classification_level = models.TextField(db_column='Classification Level', null=True)
    housing_facility = models.TextField(db_column='Housing Facility', null=True)
    total_bond_amount = models.TextField(db_column='TotalBondAmount', null=True)
    total_bail_amount = models.TextField(db_column='TotalBailAmount', null=True)
    published_date = models.TextField(db_column='Published Date', null=True)
    image = models.TextField(db_column='Image', null=True)
    url = models.TextField(db_column='URL', null=True)
    state = models.TextField(db_column='State', null=True)
    f_response_time = models.TextField(db_column='FOIA Response Time', null=True)
    f_status = models.TextField(db_column='FOIA Status', null=False, default="Pending")
    created_at = models.DateField(db_column='Created_At',null=False,default=datetime.today().date())
    assigned_to = models.TextField(db_column='Assigned To',null=True)

    class Meta:
        db_table = 'criminal_data'
