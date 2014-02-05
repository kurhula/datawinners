import logging
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed


def get_all_survey_responses(dbm):
    rows = dbm.load_all_rows_in_view('surveyresponse', reduce=False)
    for row in rows:
        yield SurveyResponse.new_from_doc(dbm=dbm, doc=SurveyResponse.__document_class__.wrap(row['value']))

def delete_invalid_survey_responses(db_name):
    logger = logging.getLogger(db_name)
    try:
        dbm = get_db_manager(db_name)
        documents_with_invalid_form_code = []
        for survey_response in get_all_survey_responses(dbm):
            form_code = survey_response.form_code
            try:
                get_form_model_by_code(dbm, form_code)
            except FormModelDoesNotExistsException:
                documents_with_invalid_form_code.append(survey_response.uuid)
                survey_response.delete()
                continue
        if documents_with_invalid_form_code:
            logger.info('Documents with Invalid form_code: %s' % (str(documents_with_invalid_form_code)))
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), delete_invalid_survey_responses, version=(10, 1, 3), threads=2)
