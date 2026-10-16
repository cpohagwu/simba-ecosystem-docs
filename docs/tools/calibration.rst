Calibration
===========

Harvest timing from ribbon-tagged records
-----------------------------------------

``fit_reproductive_parameters`` estimates ``harvest.threshold_dd`` and
``harvest.hazard_weeks`` with a nonparametric, discrete-time life table
rather than a continuous curve fit: a real per-cohort series is typically only
2-4 nonzero weekly bins.

* **Threshold.** Each cohort's first harvest week brackets the threshold (its
  thermal age that week is at or above it, the week before below it). The
  estimate is the value inside the most brackets -- interval censoring.
* **Hazards.** Cuts and cohorts at risk are pooled across cohorts per
  harvest week before dividing, the standard life-table estimator. Bins stop
  where too few bunches remain at risk, and the last kept bin is set to 1.0.

Cohorts are identified by tag *and* bagging week (``week - age_at_cut``), so a
ribbon colour reused across years never merges two cohorts.

.. code-block:: python

   from py_simba_pop import ParameterSet, RibbonProductionReader, WeatherProvider
   from py_simba_pop_tools.calibration import (
       fit_reproductive_parameters,
       hazards_to_shares,
       load_ribbon_observations,
   )

   params = ParameterSet.from_tixier_defaults()
   weather = WeatherProvider.from_file_and_params(f"{DATA}/weather.csv", params)
   ledger = RibbonProductionReader.read(f"{DATA}/production.csv").data

   fit = fit_reproductive_parameters(load_ribbon_observations(ledger, weather))
   fit.threshold_dd                       # 899.8 -- the synthetic farm's truth is 900
   shares = hazards_to_shares(fit.hazard_weeks)   # [0.197, 0.615, 1.0]
   params = params.override("harvest", {"threshold_dd": fit.threshold_dd, "hazard_weeks": shares})

Under the default ``"cohort"`` rate basis py-simba-pop reads the harvest
histogram as *shares* of the cohort, hence ``hazards_to_shares``; under
``"current_pool"`` it reads hazards.

Flowering and sucker selection cannot be fitted this way: desuckering records
carry no age at the event, and sucker output does not deplete a cohort, so
there is no life table to build. ``py_simba_pop_tools.evaluation`` scores them
for validation instead.

Literature parameter sets
-------------------------

``GUARIN_OCHOA_2012_SUCKER_SELECTION`` holds the follower-selection calibration
of Guarín & Ochoa (2012, *Revista Facultad Nacional de Agronomía Medellín*
65(1): 6419-6429, Table 2; Urabá, Colombia): threshold 2080 degree-days,
amplitude 0.171, peak 5.5 weeks, spread 0.379. It is a mapping for
``ParameterSet.override("sucker_selection", ...)``.
