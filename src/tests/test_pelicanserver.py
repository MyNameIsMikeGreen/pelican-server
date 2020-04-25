import json
import unittest
from unittest.mock import Mock

import pelicanserver
import statusMonitor


class PelicanServerTests(unittest.TestCase):

    def setUp(self):
        status_monitor = statusMonitor.StatusMonitor()
        command_executor = Mock()
        self.pelican_server = pelicanserver.PelicanServer(status_monitor, command_executor)
        self.pelican_server.app.config['TESTING'] = True
        self.app = self.pelican_server.app.test_client()

    def tearDown(self):
        pass

    def test_server_returns_static_homepage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        with open("testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"), "Static index.html file returned")

    def test_server_returns_index_page(self):
        response = self.app.get('/index.html', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        with open("testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"), "Static index.html file returned")

    def test_server_returns_status(self):
        response = self.app.get('/status', follow_redirects=True)
        self.assertEqual(200, response.status_code, "HTTP 200 returned")
        response_json = json.loads(response.get_data(as_text=True))
        self.assertTrue("status" in response_json, "Response contains key: status")
        self.assertTrue("lastChange" in response_json, "Response contains key: lastChange")


if __name__ == "__main__":
    unittest.main()
