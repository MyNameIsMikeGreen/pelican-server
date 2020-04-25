import unittest

import pelicanserver


class PelicanServerTests(unittest.TestCase):

    def setUp(self):
        self.pelican_server = pelicanserver.PelicanServer(None)
        self.pelican_server.app.config['TESTING'] = True
        self.app = self.pelican_server.app.test_client()

    def tearDown(self):
        pass

    def test_server_returns_static_homepage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        with open("testresources/index.html") as index_page:
            expected_content = index_page.read()
            self.assertEqual(expected_content, response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
