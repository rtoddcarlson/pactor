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

Getting started with pactor


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
