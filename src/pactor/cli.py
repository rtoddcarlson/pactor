import multiprocessing
import random
import time
import readchar
from pactor import Actor


class Monitor:
    def __init__(self, name, aggregator):
        self.name = name
        self.aggregator = aggregator
        self.current_value = -1
        self.running = False

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


class SubMonitor(Monitor):
    def read_next(self):
        super().read_next()
        print('current value for monitor %s: %s\r' % (self.name, self.current_value))


class Aggregator:
    def __init__(self):
        self.values = {}

    def notify(self, monitor_name, value, process_name):
        if monitor_name not in self.values:
            self.values[monitor_name] = []
        self.values[monitor_name].append(value)
        this_process_name = multiprocessing.current_process().name

        print('Received notification (%s) of value %s from monitor %s in process %s\r' %
              (this_process_name, value, monitor_name, process_name))


def main():
    print('Press \'q\' to quit...\r')
    agg = Actor(Aggregator())
    mon1 = Actor(Monitor('robot', agg.proxy))
    mon2 = Actor(SubMonitor('conveyor', agg.proxy))

    mon1.proxy.start_reading()
    mon2.proxy.start_reading()

    key_press = readchar.readchar()
    while key_press != 'q':
        key_press = readchar.readchar()

    print('closing.....\r')

    mon1.proxy.stop_reading()
    mon1.close()

    mon2.proxy.stop_reading()
    mon2.close()

    mon1.join()
    mon2.join()

    agg.close()
    agg.join()
