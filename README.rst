========
pactor
========

.. start-badges

| |travis|

.. |travis| image:: https://travis-ci.com/rtoddcarlson/pactor.svg?token=kUEn8LnV35Cck9sKzqic&branch=master
    :target: https://travis-ci.com/rtoddcarlson/pactor

.. end-badges

A lightweight Actor framework in Python.

* Free software: MIT license

Installation
============

::

    pip install pactor

You can also install the in-development version with::

    pip install https://github.com/rtoddcarlson/pactor/archive/master.zip


Documentation
=============

The actor model is a computational model that is useful for concurrent execution.  See: https://en.wikipedia.org/wiki/Actor_model.

pactor is a lightweight implementation of the actor model in Python, using multiprocessing.

The actor model stipulates that actors only interact with each other through messaging.  pactor implements that
restriction by building a proxy around an actor class and converting method calls into messages.

You declare an actor by using the @actor class decorator as follows:

.. code-block:: python

    @actor
    class MyActor:
        def __init__(self, name):
            self.name = name

        def some_method(self):
            ...



When instantiating an @actor class, you will not get a normal instance.  Instead you will get a wrapper that provides a proxy
for executing logic for the actor in a separate process.

Consider this simple example of a Monitor:

.. code-block:: python

    @actor
    class Monitor:
        def __init__(self, name):
            self.name = name
            self.status = 0

        def set_aggregator(self, aggregator):
            self.aggregator = aggregator

        def read_status(self):
            while True:
                self.status = fetch_status()
                self.aggregator.update_status(self.name, self.status)



And the Aggregator:

.. code-block:: python

    @actor
    class Aggregator:
        def __init__(self, name):
            self.name = name

        def update_status(self, target_name, status):


These could be used as follows:

.. code-block:: python

    def main():
        primary_mon = Monitor('primary')
        secondary_mon = Monitor('secondary)
        agg = Aggregator('aggregator')

        primary_mon.proxy.set_aggregator(agg.proxy)
        secondary_mon.proxy.set_aggregator(agg.proxy)

        primary_mon.proxy.read_status()
        secondary_mon.proxy.read_status()

        agg.join()

This simple example highlights several critical points:

* Each @actor class will actually run in a separate process
* The @actor class should be accessed through the .proxy member which is created by the decorator.
* Invoking a method on an @actor proxy does not directly invoke that method on the calling thread, but instead is wrapped as a message and passed to the actor process.

The wrapper provided by the @actor decorator exposes two key methods that can be called directly on the created instance:

    **.join()**

    Blocks the calling thread until the actor process terminates.

    **.close()**

    Signals that the actor process should discontinue processing messages and terminate.

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
