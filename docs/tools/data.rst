Data
====

Contracts
---------

A contract names a table's columns, their units, which may be blank and what a
blank means, the row key, and when a row becomes known. ``Contract.validate``
reports every problem rather than stopping at the first.

The availability lags below are defaults. Where a source reports later,
``contract.with_availability_lag(days)`` returns the contract with that
source's lag; a snapshot's manifest records the lag each table used.

=====================  =====================================================  ===========================
Contract               Columns                                                Known from (default)
=====================  =====================================================  ===========================
``RIBBON_LEDGER``      tag, date, bagged, cut, age_at_cut [, field_losses,    d + 7 days (end of week)
                       rejected, processed]
``DAILY_WEATHER``      date, tmean [, tmax, tmin, rain, rh]                   d + 1 day
``PLANT_MONITORING``   date, site, group_kind, group, variable, value, unit,  d (set the real delay)
                       n_plants
=====================  =====================================================  ===========================

Blank counts mean *not recorded*, never zero; ``age_at_cut`` is required
wherever ``cut > 0``; ``tmean`` may not be blank on any day; ``n_plants`` is
blank when sample sizes are unknown, and such values must not be averaged as
if equally weighted.

As-of snapshots
---------------

``write_snapshot(directory, {"ledger": (frame, RIBBON_LEDGER), ...}, as_of=...)``
validates each table, keeps only the rows known at ``as_of``, and writes them
with a manifest of hashes (tables and source files) and software versions. It
never overwrites. ``open_snapshot`` re-checks every hash; a backtest origin
reads ``snapshot.available("ledger", origin)`` -- the rows known at that origin
and nothing later.

A snapshot built from a later extract keeps that extract's values for older
rows: revisions made after ``as_of`` are not undone. Keep one snapshot per
extract.

Initial-population reconstruction
---------------------------------

``reconstruct_initial_population(production, weather_df, params, snapshot_week)``
estimates a farm's standing plants at a snapshot week from production and
weather records before it:

* bunched plants are observed: per colour, the bunches bagged and not yet cut
  or lost;
* vegetative plants are inferred through the model's flowering law: weekly
  follower selections are fitted (non-negative, smooth) so that their modelled
  flowering reproduces the recorded bagging, and the engine is run through the
  record with them.

On the synthetic established farm it recovers the true vegetative stock within
about 1% and the bunches per colour within 0.3%. ``spin_up_initial_population``
builds an equilibrium age structure for a number of mats when no records exist.
