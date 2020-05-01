import os
import sys
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

from pelicanserver import PelicanServer
from statusMonitor import StatusMonitor

import pytest


@pytest.fixture()
def app():
    status_monitor = StatusMonitor()
    command_executor = Mock()
    pelican_server = PelicanServer(status_monitor, command_executor)
    app = pelican_server.app
    app.config['TESTING'] = True
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
