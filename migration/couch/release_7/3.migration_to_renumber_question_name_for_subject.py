from datetime import datetime
import traceback
import urllib2
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.transport.contract.submission import Submission, SubmissionLogDocument
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration
from mangrove.datastore.entity import entity_by_short_code

SERVER = 'http://localhost:5984'
log_file = open('migration_release_7_3.log', 'a')

init_migrations('dbs_migrated_release_7_3.csv')

def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)

db_names = all_db_names(SERVER)

# excluding the following
# doc.form_code != 'reg' - to ignore the registration form model
# doc.is_registration_model - to ignore programmatic questionnaire
map_form_model_for_subject_questionnaires = """
function(doc) {
    if (doc.document_type == 'FormModel' && doc.form_code != 'reg'
        && doc.is_registration_model && !doc.void) {
        var existing_names = [];
        for (var i in doc.json_fields){
            var field = doc.json_fields[i];
            if (existing_names.indexOf(field.name) != -1){
	            emit(doc.form_code, doc);
            }
            existing_names.push(field.name);
        }
    }
}"""


map_submission_log_datarecord_id = """
function(doc){
    if (doc.document_type == 'SubmissionLog' && doc.status) {
        emit([doc.data_record_id, doc.form_model_revision], doc);
    }
}"""

map_datarecord_by_form_code = """
function(doc){
    if (doc.document_type == 'DataRecord' && !doc.void && doc.submission.form_code) {
        emit([doc.submission.form_code, Object.keys(doc.data).length], doc);
    }
}"""

map_entity_by_id = """
function(doc){
    if (doc.document_type == 'Entity' && !doc.void) {
        emit(doc._id, doc);
    }
}"""

def get_instance_from_doc(manager, value, classname=FormModel, documentclassname=FormModelDocument):
    doc = documentclassname.wrap(value)
    instance = classname.new_from_doc(manager, doc)
    return instance

def renumber_fields_name(form_model):
    data_to_restore, max_question_names, existing_names = [],[],{}
    data_length = 0
    for field in form_model.fields:
        if field.name.startswith("Question "):
            max_question_names.append(int(field.name[9:]))
        if field.name in existing_names:
            current_code = existing_names.get(field.name)
            question_number = max(max_question_names) + 1
            field.set_name("Question %s" % str(question_number))
            max_question_names.append(question_number)
            data_to_restore.extend([field.code, current_code])
        else:
            data_length += 1
        existing_names.update({field.name:field.code})
    return data_to_restore, data_length


def migrate_entity(manager, form_model, datarecord_doc, data_to_restore):
    submission_log_doc = manager.database.query(map_submission_log_datarecord_id, key=[datarecord_doc['value']['_id'], form_model.revision ])
    if len(submission_log_doc.rows):
        submission_log = get_instance_from_doc(manager, submission_log_doc.rows[0]['value'], classname=Submission, documentclassname=SubmissionLogDocument)
        entity_uid = datarecord_doc['value']['data']['short_code']['value']
        entity = entity_by_short_code(manager, entity_uid, form_model.entity_type)
        cleaned_data, errors = form_model.validate_submission(values=submission_log.values)
        data = [(form_model._get_field_by_code(code).name, cleaned_data.get(code), form_model._get_field_by_code(code).ddtype)
            for code in data_to_restore]
        entity.update_latest_data(data)
        entity.save()

def migrate_db(database):
    log_statement(
        '\nStart migration on database : %s \n' % database)
    try:
        manager = get_db_manager(server=SERVER, database=database)
        subject_form_model_docs = manager.database.query(map_form_model_for_subject_questionnaires)
        mark_start_of_migration(database)
        for form_model_doc in subject_form_model_docs:
            form_model = get_instance_from_doc(manager, form_model_doc['value'])
            log_statement(
                "Process on :form_model document_id : %s , form code : %s" % (form_model.id, form_model.form_code))
            data_to_restore, current_data_length = renumber_fields_name(form_model)
            datarecord_docs = manager.database.query(map_datarecord_by_form_code, key=[form_model.form_code, current_data_length])
            
            for datarecord_doc in datarecord_docs :
                migrate_entity(manager, form_model, datarecord_doc, data_to_restore)
            
            form_model.save()
            log_statement(
                "End process on :form_model document_id : %s , form code : %s" % (form_model.id, form_model.form_code))
        log_statement(
            '\nEnd migration on database : %s\n' % database)
    except Exception as e:
        log_statement('error:%s:%s\n' % (e.message, database))
        traceback.print_exc(file=log_file)

def migrate_story_2099(all_db_names):
    global skip_dbs
    print "start ...."
    log_statement(
        '\nStart ===================================================================================================\n')
    for database in all_db_names:
        try:
            if should_not_skip(database):
                migrate_db(database)
        except Exception as e:
            log_statement(":Error" + e.message)
            traceback.print_exc(file=log_file)
    log_statement(
        '\n End ====================================================================================================\n')
    print "Completed migration"


def log_statement(statement):
    print '%s : %s\n' % (datetime.utcnow(), statement)
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))

migrate_story_2099(db_names)