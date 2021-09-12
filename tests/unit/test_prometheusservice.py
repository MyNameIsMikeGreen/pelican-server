import os
import sys
import unittest
from unittest.mock import Mock, PropertyMock

from testfixtures import LogCapture

from prometheusservice import PrometheusService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))


class TestStatusMonitor(unittest.TestCase):

    def setUp(self):
        self.log_capture = LogCapture()
        self.metric_prefix = "pelican_"

    def tearDown(self):
        self.log_capture.uninstall_all()

    def test_gauge_is_set_if_metric_already_existed(self):
        # Given: metric values to set
        metric_name = "my_new_metric"
        metric_value = 0

        # And: the service is provided with the pre-existing metric
        self.mock_metric = Mock()
        self.metrics = [self.mock_metric]
        self.prometheus_service = PrometheusService(self.metric_prefix, self.metrics)

        # And: the provided gauge has matching attributes
        mock_description = Mock()
        self.mock_metric.describe.return_value = [mock_description]
        type(mock_description).name = PropertyMock(return_value=f"{self.metric_prefix + metric_name}")
        type(mock_description).type = PropertyMock(return_value="gauge")

        # When: a gauge value is set
        self.prometheus_service.gauge(metric_name, metric_value)

        # Then: the metric is set
        self.mock_metric.set.assert_called_with(metric_value)

        # And: the action is logged
        self.log_capture.check(
            ("root", "INFO", f"{self.metric_prefix + metric_name} gauge set to {metric_value}")
        )

    def test_gauge_is_set_and_metric_created_if_not_already_existed(self):
        # Given: metric values to set
        metric_name = "my_new_metric"
        metric_value = 0

        # And: the service is not provided with any metrics
        self.prometheus_service = PrometheusService(self.metric_prefix)

        # When: a gauge value is set
        self.prometheus_service.gauge(metric_name, metric_value)

        # Then: the metric is created
        self.assertEqual(self.prometheus_service.metrics[0].describe()[0].name, f"{self.metric_prefix + metric_name}")
        self.assertEqual(self.prometheus_service.metrics[0].describe()[0].type, "gauge")

        # And: the action is logged
        self.log_capture.check(
            ("root", "INFO", f"Existing gauge not found. Creating {self.metric_prefix + metric_name}"),
            ("root", "INFO", f"{self.metric_prefix + metric_name} gauge set to {metric_value}")
        )


if __name__ == "__main__":
    unittest.main()
