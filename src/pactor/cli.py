import multiprocessing
import random
import time
from sys import stdin

from pactor import actor


@actor
class Monitor:
    def __init__(self, name):
        self.name = name
        self.current_value = -1
        self.running = False

    def set_aggregator(self, aggregator):
        self.aggregator = aggregator

    def start_reading(self):
       self.running = True
       self.enqueue(self.read_next)

    def stop_reading(self):
        self.running = False

    def read_next(self):
        if not self.running:
            return

        time.sleep(random.randint(100, 5000) / 1000.0)
        process_name = multiprocessing.current_process().name
        self.current_value = random.randint(0, 100)
        self.aggregator.notify(self.name, self.current_value, process_name)
        self.enqueue(self.read_next)


@actor
class Aggregator:
    def __init__(self):
        self.values = {}

    def notify(self, monitor_name, value, process_name):
        if monitor_name not in self.values:
            self.values[monitor_name] = []
        self.values[monitor_name].append(value)
        this_process_name = multiprocessing.current_process().name

        print('Received notification (%s) of value %s from monitor %s in process %s' %
              (this_process_name, value, monitor_name, process_name))


def main():
    mon1 = Monitor('robot')
    mon2 = Monitor('conveyor')
    agg = Aggregator()

    mon1.set_aggregator(agg.proxy)
    mon2.set_aggregator(agg.proxy)

    mon1.start_reading()
    mon2.start_reading()

    key_press = stdin.read(1)
    while key_press != 'q':
        print('Pressed: %s' % (key_press,))
        key_press = stdin.read(1)

    print ('closing.....')

    mon1.stop_reading()
    mon1.close()
    mon1.join()

    mon2.stop_reading()
    mon2.close()
    mon2.join()

    agg.close()
    agg.join()
