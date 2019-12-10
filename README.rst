========
pactor
========

.. start-badges

| |travis|

.. |travis| image:: https://travis-ci.com/rtoddcarlson/pactor.svg?token=kUEn8LnV35Cck9sKzqic&branch=master
    :target: https://travis-ci.com/rtoddcarlson/pactor

.. end-badges

A minimalist actor framework in Python.

* Free software: MIT license

Installation
============

::

    pip install pactor


Running the Example
===================

Clone the repo locally, then run the following commands::

    pipenv install
    pipenv run python -m pactor

To exit, press q.

Documentation
=============

The actor model is a computational model that is useful for concurrent execution.  See: https://en.wikipedia.org/wiki/Actor_model.

pactor is a minimalist implementation of the actor model in Python, using multiprocessing.

The actor model stipulates that actors only interact with each other through messaging.  pactor implements that
restriction by building a proxy around an actor class and converting method calls into messages.

To wrap a pickleable class as an Actor, simply create an Actor with an instance of the target class, as follows:

.. code-block:: python

    class MyActor:
        def __init__(self, name):
            self.name = name

        def some_method(self):
            ...

    actor_instance = Actor(MyActor())


The Actor class provides a couple of key capabilities:
    | **.proxy**
    | A proxy object that has methods that mirror those on the wrapped class.  Calling a method on the proxy will generate a message to the actor process with the provided parameters.
    |
    | **.close()**
    | Signals that the actor process should discontinue processing messages and terminate.
    |
    | **.join()**
    | Blocks the calling thread until the actor process terminates.
    |

Additionally, the actor class itself is enhanced with an enqueue method that can be used to send messages to itself.

Consider this simple example of a Monitor:

.. code-block:: python

    class Monitor:
        def __init__(self, name, aggregator):
            self.name = name
            self.aggregator = aggregator
            self.status = 0

        def read_status(self):
            self.status = fetch_status()
            self.aggregator.update_status(self.name, self.status)
            self.enqueue(self.read_status) # queue up another read



And an Aggregator:

.. code-block:: python

    class Aggregator:
        def update_status(self, target_name, status):
            print('Status update for %s: %s' % (target_name, status))

These could be used as follows:

.. code-block:: python

    def main():
        aggregator = Actor(Aggregator('aggregator'))
        primary_mon = Actor(Monitor('primary', aggregator.proxy))
        secondary_mon = Actor(Monitor('secondary', aggregator.proxy))

        primary_mon.read_status()
        secondary_mon.read_status()

        aggregator.join()

This simple example highlights several critical points:

* Each Actor class will actually run in a separate process
* One Actor can be passed to another Actor using the .proxy member
* Invoking a method on an Actor proxy does not directly invoke that method on the calling thread, but instead is wrapped as a message and passed to the actor process.

Development
===========

To run the all tests run::

    tox

