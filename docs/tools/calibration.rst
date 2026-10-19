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

The life table keeps lost bunches at risk, so its hazards come out a little
low when field losses are frequent. The next two estimators remove them.

The field-loss rate
-------------------

``fit_field_loss_rate`` estimates ``mortality_replacement.death_rate_reproductive``
as an exposure hazard. Each week's recorded losses are taken as Poisson with
mean *rate × the bunches standing at the start of the week*.
``standing_exposure`` follows those bunches per bagging week. A cut leaves the
bagging week its age points to. Losses carry no age, so they leave the standing
bunches in proportion to their numbers, as the engine removes recorded losses.

The interval allows for overdispersion (quasi-Poisson). With ``period``
labels (a year, or a period such as a disease outbreak), each period gets its
own rate, and an F test asks whether one rate fits them all.

The engine loses no bunch in the week its cohort's harvest ends, while that
week counts in the exposure. So the fitted rate sits about 1.5 % below the one
that would reproduce the losses in the engine.

Harvest timing by maximum likelihood
------------------------------------

``fit_harvest_timing`` fits ``harvest.threshold_dd`` and the weekly hazards in
the engine's own weekly model. Of the bunches standing at the start of a week,
a share ``death_rate`` is lost. Once the cohort's thermal age has reached the
threshold, a share *h*\ :sub:`j` is cut in the *j*-th week from it. Both come
off the same bunches, so a lost bunch is never cut.

Each cohort's cuts are compared with the model *conditional on how many of its
bunches were cut*. The losses inform only the death rate (pass the rate
``fit_field_loss_rate`` found), and the timing of the cuts alone fits the
threshold and the hazards: no record is used twice.

The likelihood is a step function of the threshold, so the fit reports a
plateau of equally good thresholds and its midpoint. The search starts at 0,
where every cohort crosses in its first week and the histogram is a schedule
by age, with no response to temperature. A farm that cuts by ribbon age will
land there.

``threshold_range`` gives a quasi-likelihood range.
``bootstrap_harvest_timing`` refits on cohort-block bootstrap replicates:
blocks of consecutive bagging weeks, drawn with replacement.

.. code-block:: python

   from py_simba_pop_tools.calibration import (
       fit_field_loss_rate, fit_harvest_timing, standing_exposure,
   )

   losses = fit_field_loss_rate(standing_exposure(ledger, weather))
   losses.rate                         # 0.00138 per bunch and week
   harvest = fit_harvest_timing(load_ribbon_observations(ledger, weather), death_rate=losses.rate)
   harvest.threshold_plateau           # (899.5, 900.1): the synthetic farm's truth is 900
   harvest.hazard_weeks                # (0.200, 0.781, 1.0)
   params = losses.apply(harvest.apply(params))
   params.harvest["hazard_weeks"]      # shares [0.2, 0.625, 1.0], the farm's truth

Two shares the engine cannot reproduce are reported rather than hidden:

* ``pre_threshold_cut_share``: cuts before the threshold, fitted with their own
  weekly hazard so that a few early cuts do not set it;
* ``late_cut_share``: cuts after the histogram's last week.

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

Flowering from bagging alone
----------------------------

Some farms record bagging but neither follower selections nor a census.
``fit_flowering_split`` fits flowering's threshold, ``peak_weeks`` and
``spread`` for them, with follower selection held at given values, by
splitting the records in time:

* for each candidate flowering law, the vegetative stock at the split week is
  reconstructed from the bagging *before* it (``data.reconstruct_pre_flowering``);
* the engine then runs with no records, selecting followers by its own rule;
* only the bagging *from* the split week on is compared (Poisson deviance).

No bagging is used twice. The search is ``fit_flowering``'s, and every engine
run includes a reconstruction (about half a second), so a full fit takes some
twenty minutes.

``bootstrap_flowering_split`` gives a block bootstrap around the fitted ridge.
Peak and spread are refitted only near the ridge, and the bagging before the
split is not resampled.

.. code-block:: python

   import pandas as pd

   from py_simba_pop_tools.calibration import (
       GUARIN_OCHOA_2012_SUCKER_SELECTION, bootstrap_flowering_split,
       fit_flowering_split, split_records,
   )

   params = ParameterSet.from_tixier_defaults().override(
       "sucker_selection", GUARIN_OCHOA_2012_SUCKER_SELECTION)   # held fixed
   records = split_records(ledger, pd.read_csv(f"{DATA}/weather.csv"), params, split_week_index=260)
   start = params.override("flowering", {"peak_weeks": 4.0, "spread": 0.3})
   flowering = fit_flowering_split(records, start, thresholds=(2150, 2550, 50))
   flowering.threshold_dd, flowering.peak_weeks, flowering.spread   # 2350, 6.33, 0.467
   bootstrap_flowering_split(records, params, flowering)["threshold_dd"].quantile([0.025, 0.975])

On this synthetic farm, made by the model itself, the fit recovers the truth
(2350 degree-days, 6.35 weeks, 0.47). What identifies flowering here is the
season: thermal time makes the same delays differ in weeks through the year.
On real records, noise and model error can swamp that signal, so read the
profile and the bootstrap before trusting the estimate.

Literature parameter sets
-------------------------

``GUARIN_OCHOA_2012_SUCKER_SELECTION`` holds the follower-selection calibration
of Guarín & Ochoa (2012, *Revista Facultad Nacional de Agronomía Medellín*
65(1): 6419-6429, Table 2; Urabá, Colombia): threshold 2080 degree-days,
amplitude 0.171, peak 5.5 weeks, spread 0.379. It is a mapping for
``ParameterSet.override("sucker_selection", ...)``.
