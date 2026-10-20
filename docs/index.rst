py-simba-pop-tools
==================

Calibration, validation and backtesting tools for
`py-simba-pop <https://py-simba-pop.readthedocs.io>`_, the Python
implementation of the SIMBA-POP banana cohort model:

* **calibration** -- harvest timing from ribbon-tagged records (a life table,
  and a maximum-likelihood fit with field losses competing), the field-loss
  rate, and flowering and follower-selection timing, with bootstraps for
  their uncertainty;
* **evaluation** -- rolling-origin backtests on as-of data, with
  persistence, seasonal-naive and Mode B baselines and a calibrated Mode B,
  scored by horizon and compared with a Diebold-Mariano test;
* **data** -- the canonical tables' contracts, as-of snapshots and
  initial-population reconstruction.

.. code-block:: bash

   python -m pip install py-simba-pop-tools

Every example uses the synthetic farms of
`py-simba-pop-docs <https://github.com/cpohagwu/py-simba-pop-docs/tree/main/docs/examples/data>`_
(``docs/examples/data/synthetic``), whose truth is known.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   tools/index
   attribution
