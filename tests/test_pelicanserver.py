import json
import os
import sys
import unittest
from unittest.mock import Mock

from automaticdeactivator import AutomaticDeactivator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

import pelicanserver
from statusMonitor import StatusMonitor, Status

AUTOMATIC_DEACTIVATOR_TIMEOUT_SECONDS = 3


class TestPelicanServer(unittest.TestCase):

    def setup_server(self, status_monitor=StatusMonitor(), command_executor=StatusMonitor):
        automatic_deactivator = AutomaticDeactivator(command_executor, status_monitor, AUTOMATIC_DEACTIVATOR_TIMEOUT_SECONDS)
        self.pelican_server = pelicanserver.PelicanServer(status_monitor, command_executor, automatic_deactivator)
        self.pelican_server.app.config['TESTING'] = True
        self.app_client = self.pelican_server.app.test_client()

    def test_server_returns_static_homepage(self):
        self.setup_server(command_executor=Mock())
        response = self.app_client.get('/', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        with open("testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"), "Static index.html file returned")

    def test_server_returns_index_page(self):
        self.setup_server(command_executor=Mock())
        response = self.app_client.get('/index.html', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        with open("testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"), "Static index.html file returned")

    def test_server_returns_status(self):
        self.setup_server(command_executor=Mock())
        response = self.app_client.get('/status', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertTrue("status" in response_json, "Response contains key: status")
        self.assertTrue("lastChange" in response_json, "Response contains key: lastChange")
        self.assertTrue("lastChangeBy" in response_json, "Response contains key: lastChangeBy")

    def test_server_returns_activation_response_when_activation_occurs(self):
        status_monitor = Mock()
        status_monitor.status = Status.DEACTIVATED
        self.setup_server(status_monitor, Mock())
        response = self.app_client.get('/actions/activate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "activated"}, response_json, "Response states that the system is now activated")

    def test_server_returns_deactivation_response_when_deactivation_occurs(self):
        status_monitor = Mock()
        status_monitor.status = Status.ACTIVATED
        self.setup_server(status_monitor, Mock())
        response = self.app_client.get('/actions/deactivate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "deactivated"}, response_json, "Response states that the system is now deactivated")

    def test_server_returns_no_change_response_when_activation_called_and_already_active(self):
        status_monitor = Mock()
        status_monitor.status = Status.ACTIVATED
        self.setup_server(status_monitor, Mock())
        response = self.app_client.get('/actions/activate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "already activated; no change"}, response_json, "Response states no change")

    def test_server_returns_deactivation_response_when_previously_activated(self):
        status_monitor = Mock()
        status_monitor.status = Status.DEACTIVATED
        self.setup_server(status_monitor, Mock())
        response = self.app_client.get('/actions/deactivate', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual({"result": "already deactivated; no change"}, response_json, "Response states no change")


if __name__ == "__main__":
    unittest.main()
