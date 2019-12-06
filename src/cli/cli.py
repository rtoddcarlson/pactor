import multiprocessing
import random
import time
from pactor import actor


@actor
class Ponger:
    def __init__(self, name):
        self.name = name

    def set_pinger(self, pinger):
        self.pinger = pinger

    def pong(self, count):
        count += 1
        proc_name = multiprocessing.current_process().name
        print('ponging %s with count %s in %s' % (self.name, count, proc_name))
        time.sleep(random.randint(10, 500) / 1000.0)
        self.pinger.ping(count)


@actor
class Pinger:
    def __init__(self, name):
        self.name = name

    def set_ponger(self, ponger):
        self.ponger = ponger

    def ping(self, count):
        count += 1
        proc_name = multiprocessing.current_process().name
        print('pinging %s with count %s in %s' % (self.name, count, proc_name))
        time.sleep(random.randint(10, 500) / 1000.0)
        self.ponger.pong(count)


def main():
    ping1 = Pinger('ping one')
    ping2 = Pinger('ping two')

    pong1 = Ponger('pong one')
    pong2 = Ponger('pong two')

    ping1.proxy.set_ponger(pong1.proxy)
    ping2.proxy.set_ponger(pong2.proxy)

    pong1.proxy.set_pinger(ping2.proxy)
    pong2.proxy.set_pinger(ping1.proxy)

    ping1.proxy.ping(0)
    ping1.join()
