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

Flowering and follower selection
--------------------------------

Desuckering records carry no age at the event, so these two processes have no
life table. They are fitted through the model instead: under the default
``"cohort"`` rate basis every follower selected in week *b* becomes a
vegetative cohort that flowers, and has one follower of its own selected,
along timing curves set by a threshold (degree-days), ``peak_weeks`` and
``spread``. The curves are rescaled to total one, so their amplitudes cannot
be estimated; the fits leave them as they are.

``fit_flowering`` and ``fit_sucker_selection`` drive the engine with the
recorded selections and compare its weekly predictions with the records:
flowering with bagging, and selections for mothers that have and have not
flowered with the parous and nulliparous counts (fit flowering first: the split
depends on it). The objective is the Poisson deviance. Its profile over the
threshold has a ridge (a later threshold with an earlier peak gives nearly the
same total delay) and a narrow basin (a threshold decides the week each cohort
crosses it, so only thresholds within a few degree-days of the best one put
every cohort in the right week). The search therefore fits ``peak_weeks`` and
``spread`` on a coarse threshold grid, scans every degree-day with peak and
spread taken from that ridge, and fits fully at the deepest dips of the scan.
The fit keeps the profile and the scan.

.. code-block:: python

   from datetime import date

   from py_simba_pop import (
       ParameterSet, PopulationInventoryReader, RibbonProductionReader,
       SuckerSelectionReader, WeatherProvider,
   )
   from py_simba_pop_tools.calibration import (
       fit_flowering, fit_sucker_selection, selection_records,
   )

   params = ParameterSet.from_tixier_defaults()
   farm = f"{DATA}_new_plantation"            # the synthetic farm planted from scratch
   weather = WeatherProvider.from_file_and_params(f"{farm}/weather.csv", params)
   records = selection_records(
       weather,
       PopulationInventoryReader.read(f"{farm}/initial_population.csv").data,
       weather.week_index_for_date(date(2019, 4, 29)),  # the census / planting snapshot
       SuckerSelectionReader.read(f"{farm}/sucker_selection.csv").data,
       RibbonProductionReader.read(f"{farm}/production.csv").data,
   )
   flowering = fit_flowering(records, params, thresholds=(2160, 2560, 25))
   params = flowering.apply(params)          # 2350 degree-days, 6.35 weeks, 0.47
   selection = fit_sucker_selection(records, params, thresholds=(1890, 2290, 25))
   selection.threshold_dd                    # 2080 -- the farm's practice (Guarín & Ochoa 2012)
   selection.threshold_range(3.84)           # thresholds within 3.84 of the best deviance

The records must include follower selections (parous and nulliparous) and the
starting vegetative stock by age; bagging is taken as recorded in the week of
flowering. How well real records determine the thresholds depends on how much
the selections vary and on recording error: see the profile.

Literature parameter sets
-------------------------

``GUARIN_OCHOA_2012_SUCKER_SELECTION`` holds the follower-selection calibration
of Guarín & Ochoa (2012, *Revista Facultad Nacional de Agronomía Medellín*
65(1): 6419-6429, Table 2; Urabá, Colombia): threshold 2080 degree-days,
amplitude 0.171, peak 5.5 weeks, spread 0.379. It is a mapping for
``ParameterSet.override("sucker_selection", ...)``.
