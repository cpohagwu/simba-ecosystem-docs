Evaluation
==========

``evaluate_aggregate_curve_match(predicted, observed, max_lag_weeks=12)`` scans
lags in [-12, 12] weeks for the one that maximises Pearson's r between the
shifted prediction and the observation, and reports r, the RMSE and the ratio
of totals at that lag. Both series are indexed by integer week and reindexed
onto their common range, with gaps read as zero. It is a validation score, not
a parameter fit.

.. code-block:: python

   from py_simba_pop_tools.evaluation import evaluate_aggregate_curve_match

   match = evaluate_aggregate_curve_match(simulated_weekly_bagging, recorded_weekly_bagging)
   match.best_lag_weeks, match.correlation_at_best_lag, match.total_ratio

Rolling-origin backtests
------------------------

``evaluation.backtest`` forecasts the bunches cut in each of the next weeks
from a series of origins. At every origin a forecaster sees only the rows
known then.

* ``FarmTables(production, weather_df, weather)`` holds a farm's full records.
  ``as_of(origin)`` keeps only the rows known by the origin's start, using each
  table's availability lag (ledger 7 days, weather 1 day by default; pass other
  contracts to change them).
* The ``AsOfData`` that a forecaster receives also carries ``state_week_index``,
  the week after the last one with a known ledger row. Forecasters build the
  farm's state there, so a lag longer than a week is forecast through rather
  than read as empty weeks.

The forecasters:

* ``Persistence`` and ``SeasonalNaive``;
* ``ModeBForecaster(params)``: py-simba-pop from the state reconstructed from
  the as-of ledger, run on the as-of weather extended with its own
  climatology, so no future weather is used. With ``refit_harvest=True``,
  harvest timing is first refitted by the life table;
* ``CalibratedModeB(params)``: the field-loss rate (over the last
  ``loss_weeks`` weeks) and harvest timing by maximum likelihood, both
  refitted as of every origin, the rest from ``params``.

``run_backtest`` returns one row per origin, horizon and forecaster. Horizon 1
is the origin week.

* ``score`` gives the MAE, RMSE and bias by horizon, or by any other column.
* ``compare_forecasters`` runs a Diebold-Mariano test of equal expected loss
  at each horizon, with the Harvey, Leybourne & Newbold (1997) small-sample
  correction, and Holm-adjusts the p-values across horizons.

.. code-block:: python

   import pandas as pd
   from py_simba_pop_tools.evaluation import (
       CalibratedModeB, FarmTables, ModeBForecaster, Persistence, compare_forecasters, run_backtest, score,
   )

   weather_df = pd.read_csv(f"{DATA}/weather.csv")
   farm = FarmTables(ledger, weather_df, weather)
   forecasters = [Persistence(weather), ModeBForecaster(params), CalibratedModeB(params)]
   results = run_backtest(farm, forecasters, origins=range(300, 340), horizons=13)
   score(results)
   compare_forecasters(results, "mode_b_calibrated", "persistence")

Decide the comparisons and the criteria before looking at the results, and
apply them once.
