# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods

from mangrove.transport.player.player import SMSPlayer
from datawinners.custom_report_router.report_router import ReportRouter

from datawinners.location.LocationTree import get_location_tree
from datawinners.submission.models import  SMSResponse

import logging
from datawinners.location.LocationTree import get_location_hierarchy
from datawinners.utils import get_organization
from datawinners.messageprovider.handlers import create_failure_log
from datawinners.submission.organization_finder import OrganizationFinder
from datawinners.submission.request_processor import    MangroveWebSMSRequestProcessor, SMSMessageRequestProcessor, SMSTransportInfoRequestProcessor
from datawinners.submission.submission_utils import PostSMSProcessorLanguageActivator, PostSMSProcessorNumberOfAnswersValidators
from datawinners.utils import  get_database_manager_for_org
from mangrove.transport.facade import Request
from datawinners.messageprovider.exception_handler import handle
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from datawinners.accountmanagement.views import is_not_expired

logger = logging.getLogger("django")

@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def sms(request):
    message = Responder().respond(request)
    return HttpResponse(message)


@login_required(login_url='/login')
@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@is_not_expired
def web_sms(request):
    message = Responder(next_state_processor=find_dbm_for_web_sms).respond(request)
    return HttpResponse(message)


def find_dbm(request):
    incoming_request = {}
    #This is the http post request. After this state, the request being sent is a python dictionary
    SMSMessageRequestProcessor().process(http_request=request, mangrove_request=incoming_request)
    SMSTransportInfoRequestProcessor().process(http_request=request, mangrove_request=incoming_request)
    organization, error = _get_organization(request)

    if error is not None:
        incoming_request['outgoing_message'] = error
        create_failure_log(error, incoming_request)
        return incoming_request

    incoming_request['dbm'] = get_database_manager_for_org(organization)
    incoming_request['organization'] = organization

    incoming_request['next_state'] = process_sms_counter
    return incoming_request


class Responder(object):
    def __init__(self, next_state_processor=find_dbm):
        self.next_state_processor = next_state_processor

    def respond(self, incoming_request):
        request = self.next_state_processor(incoming_request)
        if request.has_key('outgoing_message'):
            return request['outgoing_message']

        self.next_state_processor = request['next_state']
        return self.respond(request)


def find_dbm_for_web_sms(request):
    incoming_request = dict()
    MangroveWebSMSRequestProcessor().process(http_request=request, mangrove_request=incoming_request)
    incoming_request['organization'] = get_organization(request)
    incoming_request['next_state'] = submit_to_player
    return incoming_request


def process_sms_counter(incoming_request):
    organization = incoming_request['organization']
    organization.increment_all_message_count()
    if organization.has_exceeded_message_limit():
        incoming_request['outgoing_message'] = ugettext(
            "You have used up your 100 SMS for the trial account. Please upgrade to a monthly subscription to continue sending in data to your projects.")
        return incoming_request

    incoming_request['next_state'] = submit_to_player
    return incoming_request


def send_message(incoming_request, response):
    ReportRouter().route(incoming_request['organization'].org_id, response)


def submit_to_player(incoming_request):
    try:
        post_sms_parser_processors = [PostSMSProcessorLanguageActivator(incoming_request['dbm'], incoming_request),
                    PostSMSProcessorNumberOfAnswersValidators(incoming_request['dbm'], incoming_request)]
        sms_player = SMSPlayer(incoming_request['dbm'], get_location_tree(),
            get_location_hierarchy=get_location_hierarchy,
            post_sms_parser_processors=post_sms_parser_processors)
        mangrove_request = Request(message=incoming_request['incoming_message'],
            transportInfo=incoming_request['transport_info'])
        response = sms_player.accept(mangrove_request)
        message = SMSResponse(response).text()
        send_message(incoming_request, response)
    except DataObjectAlreadyExists as e:
        message = ugettext("%s with %s = %s already exists.") % (ugettext(e.data[2]), ugettext(e.data[0]), e.data[1])
    except Exception as exception:
        message = handle(exception, incoming_request)

    incoming_request['outgoing_message'] = message
    return incoming_request


def _get_organization(request):
    _from, _to = _get_from_and_to_numbers(request)
    return OrganizationFinder().find(_from, _to)


def _get_from_and_to_numbers(request):
    _from = request.POST["from_msisdn"]
    _to = request.POST["to_msisdn"]
    return _from, _to

