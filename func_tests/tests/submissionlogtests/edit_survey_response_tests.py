# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import  setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.submissionlogpage.submission_log_locator import  EDIT_BUTTON
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_LOGIN_PAGE, DATA_WINNER_DASHBOARD_PAGE
from tests.createquestionnairetests.create_questionnaire_data import QUESTIONNAIRE_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.smstestertests.sms_tester_data import *
from tests.submissionlogtests.edit_survey_response_data import EDITED_ANSWERS, get_sms_data_with_questionnaire_code
from tests.submissionlogtests.submission_log_data import *
from tests.createprojecttests.create_project_data import  CREATE_NEW_PROJECT_DATA

@attr('suit_3')
class TestEditSurveyResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls._login()
        cls._create_project()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def _login(cls):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        cls.navigation_page = LoginPage(cls.driver).do_successful_login_with(VALID_CREDENTIALS)

    @classmethod
    def _create_project(cls):
        cls.dashboard_page = DashboardPage(cls.driver)
        create_project_page = cls.dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(CREATE_NEW_PROJECT_DATA)
        create_project_page.continue_create_project()
        CreateQuestionnairePage(cls.driver).create_questionnaire_with(QUESTIONNAIRE_DATA)
        create_project_page.save_and_create_project_successfully()


    @attr('functional_test')
    def test_should_edit_a_submission(self):
        project_name,questionnaire_code = self._get_project_details()
        self._submit_sms_data(get_sms_data_with_questionnaire_code(questionnaire_code))

        submission_log_page = self._navigate_to_submission_log_page_from_project_dashboard(project_name=project_name)
        submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(EDIT_BUTTON)

        submission_page = WebSubmissionPage(self.driver)
        submission_page.fill_and_submit_answer(EDITED_ANSWERS)
        submission_log_page = submission_page.navigate_to_submission_log()

        actual_data = submission_log_page.get_all_data_on_nth_row(1)
        expected_data=[u'Testwp02',u'25.12.2013',u'8.0',u'24.12.2012',u'LIGHT YELLOW',u'admin1',u'Aquificae, Chlorobia',u'-18 27']
        self.assertEquals(actual_data[3:],expected_data)

    def _navigate_to_submission_log_page_from_project_dashboard(self, project_name=PROJECT_NAME):
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        view_all_project_page = self.navigation_page.navigate_to_view_all_project_page()
        project_overview_project = view_all_project_page.navigate_to_project_overview_page(project_name)
        data_page = project_overview_project.navigate_to_data_page()
        submission_log_page = data_page.navigate_to_all_data_record_page()
        return submission_log_page

    def _get_project_details(self):
        overview_page = ProjectOverviewPage(self.driver)
        return overview_page.get_project_title(), overview_page.get_questionnaire_code()

    def _submit_sms_data(self, sms_data):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        page = SMSTesterPage(self.driver)
        page.send_sms_with(sms_data)
        self.assertEqual(page.get_response_message(), fetch_(MESSAGE, from_(sms_data)))
        return self._navigate_to_submission_log_page_from_project_dashboard()
