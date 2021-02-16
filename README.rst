nexrates
========

Naira Exchange Rates (nexrates) is a free API service for current and historic Naira exchange rates
published by the `Central Bank of Nigeria (CBN) <https://cbn.gov.ng/rates/>`_.

*This is inspired and based off the excellent* `exchangeratesapi <https://exchangeratesapi.io>`_
*open source* `project <https://github.com/exchangeratesapi>`_.


Usage
-----

**Latest and specific date rates**

Get the latest Naira exchange rates.

.. code-block:: bash

    GET /api/latest

Get historical rates for any date since 2001.

.. code-block:: bash

    GET /api/2021-01-01

Request specific exchange rates by setting the symbols parameter.

.. code-block:: bash

    GET /api/latest?symbol=USD&symbol=GBP

**Rates history**

Get historical rates for a time period.

.. code-block:: bash

    GET /api/history?start_at=2020-01-01&end_at=2020-01-30

Limit results to specific exchange rates to save bandwidth with the symbols parameter.

.. code-block:: bash

    GET /api/history?start_at=2020-01-01&end_at=2020-01-30&symbol=USD&symbol=GBP


Stack
-----

The API service is build upon FastAPI_ to handle requests asynchronously in order to achieve high
throughput. Other libraries used include:

- FastAPI_
- `GINO <https://python-gino.org/>`_
- `asyncpg <https://github.com/MagicStack/asyncpg>`_
- `requests <https://requests.readthedocs.io/>`_
- `APScheduler <https://apscheduler.readthedocs.io/>`_


License
-------

BSD 2-Clause


.. _FastAPI: https://fastapi.tiangolo.com/
