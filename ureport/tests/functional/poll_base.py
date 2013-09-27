import time

from poll.models import Poll
from ureport.tests.functional.admin_helper import fill_form
from ureport.tests.functional.poll_assertions import PollAssertions
from ureport.tests.functional.admin_helper import rows_of_table_by_class
from ureport.tests.functional.admin_base import AdminBase


class PollBase(PollAssertions, AdminBase):
    def start_poll(self, poll_id):
        self.open("/view_poll/%s " % poll_id)

        self.assertTrue(self.browser.is_text_present('Start Poll', 10))
        self.browser.find_link_by_text('Start Poll').first.click()
        time.sleep(2) #Sending questions is an asynchronous process

    def close_poll(self, poll_id):
        self.open("/view_poll/%s" % poll_id)

        self.assertTrue(self.browser.is_text_present('Close Poll', 10))
        self.browser.find_link_by_text('Close Poll').first.click()


    def get_poll(self, poll_id):
        return Poll.objects.get(id=poll_id)

    def respond_to_the_started_poll(self, sender, message):
        self.open('/router/console/')
        rows_responses = rows_of_table_by_class(self.browser, "messages module")
        number_of_responses = len(rows_responses)

        form_data = {
            "text": message,
            "sender": sender
        }
        fill_form(self.browser, form_data, True)
        self.browser.find_by_css("input[type=submit]").first.click()

        self.assert_that_number_of_responses_increase_by(number_of_responses, 1)


    def get_poll_response_location(self, response):
        contact = response.message.connection.contact
        location = contact.reporting_location
        return location.name

    def get_first_poll_response_location(self, poll):
        responses = self.get_poll_responses(poll)
        return self.get_poll_response_location(responses[0])

    def get_poll_responses(self, poll):
        responses = poll.responses.all()
        return responses

    def create_poll(self, name, type, question, group):
        self.open("/createpoll")
        form_data = {
            "id_type": type,
            "id_name": name,
            "id_groups": group
        }
        self.browser.fill("question_en", question)
        fill_form(self.browser, form_data)
        self.browser.find_by_css(".buttons a").last.click()

        return self.browser.url.split('/')[-2]

    def setup_poll(self, question="What is your name", number_prefix="079433934"):
        self.create_group("groupFT")
        self.create_backend("console")
        self.create_contact("FT1", "Male", "console", "%s4" % number_prefix, "groupFT")
        self.create_contact("FT2", "Male", "console", "%s5" % number_prefix, "groupFT")

        poll_id = self.create_poll(question, "Yes/No Question", question, "groupFT")

        return poll_id, question

    def reassign_poll_response(self, poll_id, second_poll_id):
        self.open("/%s/responses/" % poll_id)
        responses_all = self.browser.find_by_id("input_select_all").first
        responses_all.check()
        elements = self.browser.find_by_id("id_poll")
        elements.first.find_by_value(second_poll_id).first._element.click()
        assign_link = self.browser.find_link_by_text("Assign selected to poll")
        assign_link.click()
        time.sleep(7)

    def reply_poll_to_an_ureporter(self, poll_id, message):
        self.open("/%s/responses/" % poll_id)
        responses_all = self.browser.find_by_id("input_select_all").first
        responses_all.check()
        self.browser.fill("text", message)
        reply_link = self.browser.find_link_by_text("Reply to selected")
        reply_link.click()
        time.sleep(5)








