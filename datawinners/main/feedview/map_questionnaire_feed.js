function (doc) {
    if (doc.document_type == 'EnrichedSurveyResponse') {
        var result = {'id':doc.survey_response_id, 'data_sender_id':doc.data_sender['id'], 'survey_response_modified_time':doc.survey_response_modified_time};
        var output_values = doc.values;
        if (doc.status == 'success') {
            output_values = success_values(doc.values)
        }
        result['values'] = output_values;
        result['status'] = status(doc);
        emit([doc.form_code, doc.survey_response_modified_time], result)
    }

    function success_values(values) {
        var result = {};
        for (key in values) {
            if (values[key].is_entity_question) {
                for (answer_key in values[key].answer)
                    result[key] = answer_key
            } else if (values[key].type == 'select1' || values[key].type == 'select') {
                var choices = []
                for (choice in values[key].answer) {
                    choices.push(choice)
                }
                result[key] = choices
            } else {
                result[key] = values[key].answer
            }
        }
        return result
    }

    function status(doc) {
        var doc_status = doc.status
        if (doc.void) {
            doc_status = 'deleted'
        }
        return doc_status
    }
}