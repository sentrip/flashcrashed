============
flashcrashed
============


.. image:: https://img.shields.io/pypi/v/flashcrashed.svg
        :target: https://pypi.python.org/pypi/flashcrashed

.. image:: https://img.shields.io/travis/sentrip/flashcrashed.svg
        :target: https://travis-ci.org/sentrip/flashcrashed

.. image:: https://readthedocs.org/projects/flashcrashed/badge/?version=latest
        :target: https://flashcrashed.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/sentrip/flashcrashed/branch/master/graph/badge.svg
     :target: https://codecov.io/gh/sentrip/flashcrashed

.. image:: https://pyup.io/repos/github/sentrip/flashcrashed/shield.svg
     :target: https://pyup.io/repos/github/sentrip/flashcrashed/
     :alt: Updates



Minimal library for detecting flash crashes in cryptocurrency prices on Bitfinex


* Free software: GNU General Public License v3
* Documentation: https://flashcrashed.readthedocs.io.


Features
--------

* CLI for monitoring cryptocurrency prices for flash crashes
* CLI for testing performance of a flash crash detector
* Configurable flash crash detector for custom price monitoring


Installation
------------
To install flashcrashed, do:

.. code-block:: shell

    pip install flashcrashed


Basic Usage
-----------

To use flashcrashed, do:

.. code-block:: shell

    flashcrashed <BITFINEX_KEY> <BITFINEX_SECRET>


To test the performance of a detector, do:

.. code-block:: shell

    flashtest

The default detector used is the detector.SimpleDetector. To use your own:

.. code-block:: python

    # my_detector.py
    from flashcrashed.detector import Detector

    class CustomDetector(Detector):
        def predict(self, price):
            # Return: 0 - BUY, 1 - HOLD (do nothing), 2 - SELL
            return 1


To test its performance:

.. code-block:: shell

    flashtest --detector my_detector.CustomDetector


To run flashcrashed with custom detector:

.. code-block:: shell

    flashcrashed --detector my_detector.CustomDetector



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
