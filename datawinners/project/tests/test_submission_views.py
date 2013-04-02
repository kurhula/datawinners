import unittest
from django.http import HttpRequest
from mock import Mock, patch
from mangrove.datastore.documents import SubmissionLogDocument
from mangrove.transport.contract.submission import Submission
from mangrove.utils.dates import utcnow
from project.views.submission_views import build_static_info_context

class TestSubmissionViews(unittest.TestCase):
    def test_should_get_static_info_from_submission(self):
        with patch("project.views.submission_views.get_data_sender") as get_data_sender:
            get_data_sender.return_value = ('Psub', 'rep2', 'tester@gmail.com')
            created_time = utcnow()
            submission_document = SubmissionLogDocument(source='tester@gmail.com', channel='web', status=False,
                event_time=created_time,error_message="Some Error in submission")
            submission = Submission(Mock())
            submission._doc = submission_document
            static_info = build_static_info_context(Mock(), Mock(spec=HttpRequest), submission)
            SUBMISSION_DATE_FORMAT = "%b. %d, %Y, %I:%M %p"
            expected_values = {'static_content':{
                               'Data Sender': ('Psub', 'rep2', 'tester@gmail.com'),
                               'Source': 'Web',
                               'Status': 'Error. Some Error in submission',
                               'Submission Date': created_time.strftime(SUBMISSION_DATE_FORMAT)
                               },'is_edit':True}
            self.assertEqual(expected_values, static_info)