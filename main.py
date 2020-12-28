import re
from os import environ
from time import sleep

from prometheus_client.exposition import start_http_server
from prometheus_client.metrics_core import Metric
from prometheus_client.registry import REGISTRY
from requests import get

SCRAPE_URL = environ.get('SCRAPE_URL', "http://localhost:5555")
METRIC_PORT = int(environ.get('METRIC_PORT', 8000))


class JsonCollector:
    def __init__(self, endpoint):
        self._endpoint = endpoint
        self.subst = re.compile(r"[^a-zA-Z0-9_:]+")

    def collect(self):
        # Fetch the JSON
        try:
            response = get(self._endpoint).json()
            # Metrics with labels for the documents loaded
            metric = Metric('remote_sensor_monitor', 'Sensor info', 'gauge')
            for r in response:
                sensor_app = self.subst.sub("_", r['SensorApp'])
                metric.add_sample(
                    f"remote_sensor_monitor_{sensor_app}", value=r['SensorValue'], labels={
                        'SensorClass': r['SensorClass'],
                        'SensorName': r['SensorName'],
                        'SensorUnit': r['SensorUnit']
                    }
                )
            yield metric
        except Exception as e:
            print(f"Ran into exception: {e}")


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(METRIC_PORT)
    REGISTRY.register(JsonCollector(SCRAPE_URL))
    print(f"Started server to scrape {SCRAPE_URL} exposed on port {METRIC_PORT}!")
    while True:
        sleep(10)
