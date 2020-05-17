import json
import os
import sys
import unittest
from subprocess import CalledProcessError
from unittest.mock import Mock, call, ANY

from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

import pelicanserver
from statusMonitor import StatusMonitor, Status

AUTOMATIC_DEACTIVATOR_TIMEOUT_SECONDS = 3


class TestPelicanServer(unittest.TestCase):

    def setUp(self):
        self.log_capture = LogCapture()

    def tearDown(self):
        self.log_capture.uninstall_all()

    def setup_server(self, status_monitor=StatusMonitor(), command_executor=Mock(), automatic_deactivator=Mock()):
        self.pelican_server = pelicanserver.PelicanServer(status_monitor, command_executor, automatic_deactivator)
        self.pelican_server.app.config['TESTING'] = True
        self.app_client = self.pelican_server.app.test_client()

    def test_server_returns_static_homepage(self):
        self.setup_server()
        response = self.app_client.get('/', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        with open(os.path.dirname(__file__) + "/testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"), "Static index.html file returned")

    def test_server_returns_index_page(self):
        self.setup_server()
        response = self.app_client.get('/index.html', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        with open(os.path.dirname(__file__) + "/testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"), "Static index.html file returned")

    def test_server_returns_status(self):
        self.setup_server()
        response = self.app_client.get('/status', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertTrue("status" in response_json, "Response contains key: status")
        self.assertTrue("lastChange" in response_json, "Response contains key: lastChange")
        self.assertTrue("lastChangeBy" in response_json, "Response contains key: lastChangeBy")
        self.assertTrue("scheduledDeactivation" in response_json, "Response contains key: scheduledDeactivation")

    def test_server_returns_activation_response_when_activation_occurs(self):
        status_monitor = Mock()
        status_monitor.status = Status.DEACTIVATED
        automatic_deactivator = Mock()
        command_executor = Mock()
        self.setup_server(
            status_monitor=status_monitor,
            automatic_deactivator=automatic_deactivator,
            command_executor=command_executor
        )
        response = self.app_client.get('/actions/activate', follow_redirects=True)
        command_executor.activate.assert_called_with()
        status_monitor.set_status.assert_called_with(Status.ACTIVATED, scheduled_deactivation=ANY)
        automatic_deactivator.reset_timer.assert_called_with(None)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "activated"}, response_json, "Response states that the system is now activated")

    def test_server_returns_activation_response_when_activation_occurs_with_custom_timeout(self):
        status_monitor = Mock()
        status_monitor.status = Status.DEACTIVATED
        automatic_deactivator = Mock()
        command_executor = Mock()
        self.setup_server(
            status_monitor=status_monitor,
            automatic_deactivator=automatic_deactivator,
            command_executor=command_executor
        )
        response = self.app_client.get('/actions/activate?timeout_seconds=1', follow_redirects=True)
        command_executor.activate.assert_called_with()
        status_monitor.set_status.assert_has_calls(
            calls=[call(Status.MODIFYING),
                   call(Status.ACTIVATED, scheduled_deactivation=ANY)])
        automatic_deactivator.reset_timer.assert_called_with(1)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "activated"}, response_json, "Response states that the system is now activated")

    def test_server_returns_deactivation_response_when_deactivation_occurs(self):
        status_monitor = Mock()
        status_monitor.status = Status.ACTIVATED
        automatic_deactivator = Mock()
        command_executor = Mock()
        self.setup_server(
            status_monitor=status_monitor,
            automatic_deactivator=automatic_deactivator,
            command_executor=command_executor
        )
        response = self.app_client.get('/actions/deactivate', follow_redirects=True)
        command_executor.deactivate.assert_called_with()
        status_monitor.set_status.assert_has_calls(
            calls=[call(Status.MODIFYING),
                   call(Status.DEACTIVATED, scheduled_deactivation=ANY)])
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "deactivated"}, response_json, "Response states that the system is now deactivated")

    def test_server_returns_no_change_response_when_activation_called_and_already_activated(self):
        status_monitor = Mock()
        status_monitor.status = Status.ACTIVATED
        self.setup_server(status_monitor=status_monitor)
        response = self.app_client.get('/actions/activate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "already activated; no change"}, response_json, "Response states no change")

    def test_server_returns_deactivation_response_when_deactivation_called_and_already_deactivated(self):
        status_monitor = Mock()
        status_monitor.status = Status.DEACTIVATED
        self.setup_server(status_monitor=status_monitor)
        response = self.app_client.get('/actions/deactivate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "already deactivated; no change"}, response_json, "Response states no change")

    def test_server_returns_modifying_response_when_activation_called_and_already_modifying(self):
        status_monitor = Mock()
        status_monitor.status = Status.MODIFYING
        self.setup_server(status_monitor=status_monitor)
        response = self.app_client.get('/actions/activate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "system already modifying; no change"}, response_json, "Response states no change")

    def test_server_returns_modifying_response_when_deactivation_called_and_already_modifying(self):
        status_monitor = Mock()
        status_monitor.status = Status.MODIFYING
        self.setup_server(status_monitor=status_monitor)
        response = self.app_client.get('/actions/deactivate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "system already modifying; no change"}, response_json, "Response states no change")

    def test_server_aborts_on_failed_startup(self):
        command_executor = Mock()
        command_executor.deactivate.side_effect = CalledProcessError(-1, ":")
        with self.assertRaises(SystemExit):
            self.setup_server(status_monitor=Mock(), command_executor=command_executor)
        self.log_capture.check(
            ('root', 'CRITICAL', 'Failed to deactivate upon startup of Pelican Server. '
                                 'MiniDLNA may not be installed. Aborting...')
        )


if __name__ == "__main__":
    unittest.main()
