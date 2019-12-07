import random
import time
from pactor import actor


@actor
class Monitor:
    def __init__(self, name):
        self.name = name
        self.current_value = -1

    def set_aggregator(self, aggregator):
        self.aggregator = aggregator

    def run_monitor(self):
        while True:
            time.sleep(random.randint(100, 5000) / 1000.0)
            self.current_value = random.randint(0, 100)
            self.aggregator.notify(self.name, self.current_value)


@actor
class Aggregator:
    def __init__(self):
        self.values = {}

    def notify(self, monitor_name, value):
        if monitor_name not in self.values:
            self.values[monitor_name] = []
        self.values[monitor_name].append(value)
        print('Received notification of value %s from monitor %s' % (value, monitor_name))


def main():
    mon1 = Monitor('robot')
    mon2 = Monitor('conveyor')
    agg = Aggregator()

    mon1.set_aggregator(agg.proxy)
    mon2.set_aggregator(agg.proxy)

    mon1.run_monitor()
    mon2.run_monitor()

    agg.join()
