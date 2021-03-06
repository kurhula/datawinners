from django.http import HttpResponse
from django_digest.decorators import httpdigest
from datawinners.dataextraction.helper import  encapsulate_data_for_form, convert_to_json_file_download_response, generate_filename
from datawinners.main.database import get_database_manager


@httpdigest
def get_for_form(request, form_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        data_for_form = encapsulate_data_for_form(dbm, form_code, start_date, end_date)
        return convert_to_json_file_download_response(data_for_form, generate_filename(form_code, start_date, end_date))
    return HttpResponse("Error. Only support GET method.")

