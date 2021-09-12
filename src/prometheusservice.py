import logging

from prometheus_client import Gauge


class PrometheusService:

    logger = logging.getLogger()

    def __init__(self, metric_prefix="pelican_", metrics=[]):
        self.metric_prefix = metric_prefix
        self.metrics = metrics

    def gauge(self, name, value):
        try:
            gauge = next(metric for metric in self.metrics if metric.describe()[0].name == f"{self.metric_prefix + name}" and metric.describe()[0].type == "gauge")
        except StopIteration:
            self.logger.info(f"Existing gauge not found. Creating {self.metric_prefix + name}")
            gauge = Gauge(self.metric_prefix + name, f"Pelican gauge {self.metric_prefix + name}")
            self.metrics.append(gauge)
        gauge.set(value)
        self.logger.info(f"{self.metric_prefix + name} gauge set to {value}")
