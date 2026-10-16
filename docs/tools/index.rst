py-simba-pop-tools
==================

=========================================  ===============================================================
Module                                     What it does
=========================================  ===============================================================
``py_simba_pop_tools.calibration``         harvest-timing life table; cited literature parameter sets
``py_simba_pop_tools.evaluation``          lag-scanned agreement between a simulated and an observed series
``py_simba_pop_tools.data``                data contracts, as-of snapshots, initial-population reconstruction
=========================================  ===============================================================

The package reads canonical tables only -- the schemas py-simba-pop's readers
take. Converting a farm's own exports into them is the job of a separate,
farm-specific adapter.

.. toctree::
   :maxdepth: 1

   calibration
   evaluation
   data
