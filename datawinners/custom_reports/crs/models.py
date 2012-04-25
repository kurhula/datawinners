from django.db import models
from mangrove.utils.types import is_empty

def crs_model_creator(submission_data, model, question_mapping=None, defaults=None):
    if not question_mapping: question_mapping = {}
    if not defaults: defaults = {}
    _save_submission_via_model(submission_data, model,question_mapping, defaults)

way_bill_sent_mapping = {
    'q1' : 'q7',
    'q2' : 'q18',
    'q3' : 'q4',
    'q4' : 'q8',
    'q5' : 'q2',
    'q6' : 'q3',
    'q7' : 'q17',
    'q8' : 'q9',
    'q9' : 'q15',
    'q10' : 'q6'
}
way_bill_sent_by_site_mapping = {
    'q1' : 'q2',
    'q2' : 'q11',
    'q3' : 'q3',
    'q6' : 'q5',
    'q7' : 'q6',
    'q8' : 'q7',
    'q9' : 'q8',
    'q10' : 'q9'
}

class WayBillSent(models.Model):
    q1 = models.TextField(db_column='pl_code')
    q2 = models.TextField(db_column='waybill_code')
    q3 = models.DateField(db_column='sent_date')
    q4 = models.TextField(db_column='transaction_type', null=True)
    q5 = models.TextField(db_column='warehouse_code', null=True)
    q6 = models.TextField(db_column='sender_name')
    q7 = models.TextField(db_column='truck_id')
    q8 = models.TextField(db_column='food_type')
    q9 = models.FloatField(db_column='weight')
    q10 = models.TextField(db_column='receiver_code')

way_bill_received_mapping = {
    'q1' : 'q2',
    'q2' : 'q1',
    'q3' : 'q5',
    'q4' : 'q6',
    'q5' : 'q3',
    'q6' : 'q7',
    'q7' : 'q13',
    'q8' : 'q15',
    'q9' : 'q4',
    }
way_bill_received_by_site_mapping = {
    'q1' : 'q2',
    'q2' : 'q1',
    'q3' : 'q4',
    'q4' : 'q5',
    'q5' : 'q3',
    'q6' : 'q6',
    'q7' : 'q8',
    'q8' : 'q9',
    }

class WayBillReceived(models.Model):
    q1 = models.TextField(db_column='pl_code')
    q2 = models.TextField(db_column='waybill_code')
    q3 = models.TextField(db_column='site_code')
    q4 = models.TextField(db_column='receiver_name')
    q5 = models.DateField(db_column='received_date')
    q6 = models.TextField(db_column='truck_id')
    q7 = models.FloatField(db_column='good_net_weight')
    q8 = models.FloatField(db_column='damaged_net_weight')
    q9 = models.TextField(db_column='transaction_type', null=True)

sfm_distribution_mapping = {
    'q1' : 'q1',
    'q2' : 'q2',
    'q3' : 'q3',
    'q4' : 'q6',
    'q5' : 'q4',
    'q6' : 'q5',
}
sfm_distribution_defaults = {
    'distribution_type' : 'SFM'
}
sfe_distribution_mapping = {
    'q1' : 'q1',
    'q2' : 'q2',
    'q3' : 'q3',
    'q4' : 'q6',
    'q5' : 'q4',
    'q6' : 'q5',
}
sfe_distribution_defaults = {
    'distribution_type' : 'SFE'
}
ffa_distribution_mapping = {
    'q1' : 'q1',
    'q2' : 'q2',
    'q3' : 'q3',
    'q4' : 'q7',
    'q5' : 'q5',
    'q7' : 'q6',
    'q8' : 'q4',
}
ffa_distribution_defaults = {
    'distribution_type' : 'FFA'
}
class Distribution(models.Model):
    q1 = models.TextField(db_column='site_code')
    q2 = models.DateField(db_column='distribution_date')
    q3 = models.TextField(db_column='received_waybill_code')
    q4 = models.TextField(db_column='returned_waybill_code')
    q5 = models.FloatField(db_column='oil', null=True)
    q6 = models.FloatField(db_column='csb', null=True)
    q7 = models.FloatField(db_column='sorghum', null=True)
    q8 = models.FloatField(db_column='rice', null=True)
    distribution_type = models.TextField()

class PhysicalInventorySheet(models.Model):
    q1 = models.TextField(db_column='store_house_code')
    q2 = models.DateField(db_column='physical_inventory_closing_date')
    q3 = models.DateField(db_column='actual_physical_inventory_date')
    q4 = models.TextField(db_column='pl_code')
    q5 = models.TextField(db_column='food_type')
    q6 = models.FloatField(db_column='good_net_weight')
    q7 = models.FloatField(db_column='damaged_net_weight')


class SiteActivities(models.Model):
    q1 = models.TextField(db_column='fiscal_year_with_initials')
    q2 = models.TextField(db_column='site_location')
    q3 = models.TextField(db_column='site_gps_coordinates')
    q4 = models.TextField(db_column='tel_no')
    q5 = models.TextField(db_column='site_person_responsible')
    q6 = models.TextField(db_column='type_of_activity')
    q7 = models.TextField(db_column='site_code')


class Warehouse(models.Model):
    q1 = models.TextField(db_column='name')
    q2 = models.TextField(db_column='address')
    q3 = models.TextField(db_column='gps_coordinates')
    q4 = models.TextField(db_column='tel_no')
    q5 = models.TextField(db_column='initials')

bill_of_lading_mapping = {
    'q1' : 'q1',
    'q2' : 'q2',
    'q3' : 'q4',
    'q4' : 'q9',
    'q5' : 'q10',
    'q6' : 'q13',
}

class BillOfLading(models.Model):
    q1 = models.TextField(db_column='pl_code')
    q2 = models.TextField(db_column='shipment_type')
    q3 = models.DateField(db_column='issue_date')
    q4 = models.TextField(db_column='food_type')
    q5 = models.TextField(db_column='bill_of_lading_code')
    q6 = models.FloatField(db_column='weight')

break_bulk_sent_mapping = {
    'q1' : 'q2',
    'q2' : 'q13',
    'q3' : 'q16',
    'q4' : 'q6',
}

class BreakBulkSent(models.Model):
    q1 = models.DateField(db_column='sent_date')
    q2 = models.FloatField(db_column='weight')
    q3 = models.TextField(db_column='waybill_code')
    q4 = models.TextField(db_column='pl_code')

container_sent_mapping = {
    'q1' : 'q1',
    'q2' : 'q5',
    'q3' : 'q6',
}

class ContainerSent(models.Model):
    q1 = models.TextField(db_column='bill_of_lading')
    q2 = models.FloatField(db_column='weight')
    q3 = models.TextField(db_column='container_code')

break_bulk_received_at_port_mapping = {
    'q1' : 'q1',
    'q2' : 'q3',
    'q3' : 'q13',
    'q4' : 'q15',
}

container_received_at_port_mapping = {
    'q1' : 'q15',
    'q2' : 'q2',
    'q3' : 'q12',
    'q4' : 'q14',
    'q5' : 'q1',
}

class WayBillReceivedPort(models.Model):
    q1 = models.TextField(db_column='waybill_code')
    q2 = models.DateField(db_column='received_date')
    q3 = models.FloatField(db_column='good_weight')
    q4 = models.FloatField(db_column='damaged_weight')
    q5 = models.TextField(db_column='container_code', null=True)

sf_bav_mapping = {
    'q1' : 'q3',
    'q2' : 'q2',
    'q3' : 'q4',
    'q5' : 'q5',
    'q6' : 'q6',
}

ffa_bav_mapping = {
    'q2' : 'q2',
    'q3' : 'q3',
    'q4' : 'q4',
    'q5' : 'q5',
    'q7' : 'q6',
}

ffa_bav_defaults = {
    'q1' : 'FFA'
}

cps_bav_mapping = {
    'q2' : 'q2',
    'q3' : 'q3',
    'q4' : 'q4',
    'q5' : 'q5',
    'q6' : 'q6',
}

cps_bav_defaults = {
    'q1' : 'CPS'
}

class BAV(models.Model):
    q1 = models.TextField(db_column='bav_type')
    q2 = models.DateField(db_column='bav_date')
    q3 = models.IntegerField(db_column='no_of_recipients')
    q4 = models.FloatField(db_column='rice', null=True)
    q5 = models.FloatField(db_column='oil', null=True)
    q6 = models.FloatField(db_column='csb', null=True)
    q7 = models.FloatField(db_column='sorghum', null=True)

sfm_no_of_recipient_defaults = {
    'q1' : 'SFM'
}

sfe_no_of_recipient_defaults = {
    'q1' : 'SFE'
}

ffa_no_of_recipient_defaults = {
    'q1' : 'FFA'
}

cps_no_of_recipient_defaults = {
    'q1' : 'CPS'
}

class NumberOfRecipientServed(models.Model):
    q1 = models.TextField(db_column='received_type')
    q2 = models.DateField(db_column='received_date')
    q3 = models.IntegerField(db_column='no_of_type1_recipient')
    q4 = models.IntegerField(db_column='no_of_type2_recipient')
    q5 = models.IntegerField(db_column='no_of_new_type1_recipient')
    q6 = models.IntegerField(db_column='no_of_new_type2_recipient')

def convert_to_sql_compatible(param):
    if isinstance(param, list) :
        return ",".join(param)

    return param

def _convert_submission_data_to_model_fields(fields=None, submission_data=None,question_mapping=None):
    field_names = [field.name for field in fields if field.name != 'id']
    if is_empty(question_mapping):
        return  {field_name: convert_to_sql_compatible(submission_data.get(field_name)) for field_name in field_names}
    return  {field_name: convert_to_sql_compatible(submission_data.get(question_mapping.get(field_name))) for field_name in field_names}


def _save_submission_via_model(submission_data, model,question_mapping, defaults):
    model_fields = model._meta.fields
    submission_values = _convert_submission_data_to_model_fields(fields=model_fields,
        submission_data=submission_data,question_mapping=question_mapping)
    submission_values.update(defaults)
    model(**submission_values).save()
