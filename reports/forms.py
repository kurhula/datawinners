# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.forms.fields import CharField,IntegerField
from django.forms.forms import Form
from django import forms


class ReportHierarchy(Form):
    PATH_CHOICES = (("location","location"),("governance","governance"))
    FIELD_CHOICES = (("patients","patients"),("beds","beds"),("meds","meds"))
    error_css_class = 'error'
    required_css_class = 'required'
    aggregate_on_path = forms.ChoiceField(required = True,widget=forms.Select,choices=PATH_CHOICES)
    aggregates_field = forms.ChoiceField(required = True,widget=forms.Select,choices=FIELD_CHOICES)
    column_headers = list
    values = list
    level = IntegerField(min_value=1,max_value=3)
class Report(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    entity_type = CharField(required=True,label='Entity Type')
    column_headers = list
    values = list
    filter = CharField(required=False,label='Filter')
    

