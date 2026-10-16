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
