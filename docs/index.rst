SIMBA ecosystem
===============

Packages that work alongside `py-simba-pop <https://py-simba-pop.readthedocs.io>`_,
the Python implementation of the SIMBA-POP banana cohort model:

* **py-simba-pop-tools** -- calibration, validation and backtesting for
  py-simba-pop: a life-table estimate of the harvest parameters, agreement
  scores for simulated series, data contracts, as-of snapshots for backtests,
  and initial-population reconstruction.

.. note::

   py-simba-pop-tools is in development (0.1.0.dev0) and not yet on PyPI.

Every example uses the synthetic farms of
`py-simba-pop-docs <https://github.com/cpohagwu/py-simba-pop-docs/tree/main/docs/examples/data>`_
(``docs/examples/data/synthetic``), whose truth is known.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   tools/index
   attribution
