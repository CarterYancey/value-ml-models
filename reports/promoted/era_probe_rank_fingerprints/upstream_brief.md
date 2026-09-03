# Within-quarter percent ranks leak the calendar quarter — brief for upstream

*From `value-ml-models` (downstream consumer of `sharadar-dataset`), September 2026.*
*Dataset examined: `dataset_v1.0`. Everything below is reproducible from the
run ids and queries given; the probe code lives in
`value-ml-models/src/diagnostics/` (branch `claude/era-identifiability-probe`).*

## 1. Summary

The rank columns (`{name}_rank`, ADR 0008) let a tree model identify the
calendar quarter a row comes from, from a single row, with near certainty.
The carrier is not economics. It is the tie convention: a tied group's
percent rank equals the share of that quarter's cross-section sitting below
it, which is a quarter-specific constant. Every integer-valued composite
(`piotroski_f`, `mohanram_g7`) and every zero-inflated ratio
(`rnd_to_assets`, `dividend_yield`, …) therefore ships, in its rank column,
a lookup key for the quarter.

Consequences, in order of severity:

1. The diagnostic schemes `entity_holdout` and `random_kfold` are
   contaminated for rank-fed models: the model can locate the test row's
   quarter among training rows and read off that quarter's base rate. The
   registered leakage-gap experiment (decision 0010) will mostly measure this,
   not firm-identity memorisation.
2. `walkforward` and `holdout` are **not inflated** (test quarters are
   unseen, so the key has nothing to look up), but rank-fed models waste
   capacity memorising training quarters, absorb an undeclared market-state
   signal, and produce extracted rules whose thresholds mean different
   score cutoffs in different quarters.
3. The problem is structural to ranking discrete or mass-point variables
   within a cross-section; no tie convention fixes it.

We ask for a new dataset version that stops ranking integer composites and
decides, explicitly, how mass-point features are ranked; plus a build-time
audit so the property cannot silently return. Details in §6; a task
breakdown for upstream in §9.

Evidence levels used below: **[verified]** = measured directly on
`dataset_v1.0` with the query or run id given; **[inferred]** = the
mechanism follows from the documented construction and the importances,
but the specific column was not isolated in its own run; **[pending]** =
a check we have queued but not yet seen the result of.

## 2. Motivation — why we ran this

`entity_holdout` (decision 0010) holds out permaticker bucket 0 while train
and test share the same years. The worry was that a return model scored
under it could learn *which eras were good* rather than *which stocks*.
`data/manual.md` §7 registers an era-identifiability probe for exactly this:
predict the calendar year from features alone, raw vs. rank sets; beating
chance settles "you can't tell what date a sample comes from" negatively.

## 3. Method

- **Target:** `year(snapshot_date)`, derived from `key_meta`; nothing in the
  label matrix is touched, no feature is derived.
- **Split:** `entity_holdout`, fold 0, `horizon_years = 3` (the horizon
  selects the tag set and `sample_weight_3y`). Train = buckets 1–4, all
  snapshot kinds; test = bucket-0 median-kind, label-observable rows. The
  probe's rows are exactly the rows any 3y experiment fits, weighted by the
  same `sample_weight_3y`. Train and test are entity-disjoint by
  construction, so memorising firms cannot help. (Downstream has a pending
  check that the permaticker sets do not intersect; upstream can confirm
  from `splits.parquet` with the query in §8.)
- **Model:** LightGBM multiclass, 200 rounds, 31 leaves, learning rate 0.05,
  seed 7; one arm with a depth-4 decision tree for rule extraction.
- **Baselines** on the 24 training years: uniform 1/24 = 0.042; train-prior
  expected accuracy Σp² = 0.046; majority year = 0.091–0.092. Majority year
  is the one to beat: snapshot counts grow over the sample.
- **Feature arms** are ordinary manifest selections: `features` (minus the
  two filing-date fields, the Y/N flags and the classification family,
  which are non-numeric), `ranks`, `ranks` minus the `technical` family,
  and four-column subsets. No column is transformed; the model sees the
  parquet values.
- **Harness sanity check.** On the downstream test fixture, whose features
  are iid noise, the same probe scores at chance under `entity_holdout`
  and above chance only under `random_kfold` (where the three snapshot
  kinds of one stock-quarter, which share fundamentals, straddle train and
  test). The probe does not manufacture era signal on its own.

Metrics are weighted by Σ `sample_weight_3y`. "±1y" is accuracy within one
year; MAE is in years.

## 4. Results (`dataset_v1.0`, entity_holdout, 3y)

| arm (run id) | model | accuracy | ±1y | MAE (y) |
|---|---|---|---|---|
| raw `features` minus dates/flags/classification (`8a4593f4f4ae`) | LightGBM | 0.451 | 0.612 | 2.98 |
| raw, same columns (`975c93ce7338`) | tree, depth 4 | 0.248 | 0.374 | 5.05 |
| **`ranks`** (`2d3cfe09e14c`) | LightGBM | **0.954** | 0.968 | 0.24 |
| `ranks` minus `technical` family (`36968b380c93`) | LightGBM | 0.926 | 0.955 | 0.37 |
| 4 rank columns only: `piotroski_f_rank`, `mohanram_g7_rank`, `rnd_to_assets_rank`, `dividend_yield_rank` (`c3317a88e84f`) | LightGBM | **0.917** | 0.947 | 0.45 |
| the same 4 columns, raw (`de8615729c61`) | LightGBM | 0.148 | 0.322 | 5.92 |
| majority-year baseline | — | 0.091 | — | — |

Reading:

- **Ranks beat raw levels by a wide margin.** If era were carried by
  economics, nominal level drift should make the raw set at least as
  identifiable. The rank transform is *adding* information.
- **Removing the price/volume block barely matters** (0.954 → 0.926). The
  first rank-arm importances were led by `dollar_volume_3m_rank` and
  `amihud_12m_rank`; with `technical` excluded, the gain importances became
  `rnd_to_assets_rank` 0.44, `dividend_yield_rank` 0.35, `mohanram_g7_rank`
  0.074, `piotroski_f_rank` 0.043 — every one a discrete or zero-inflated
  column, no smooth fundamental among them.
- **Four rank columns alone reach 0.917.** Their raw counterparts reach
  0.148: an integer score 0–9 cannot date a row, so the residual 0.15 is
  genuine drift in the dividend-payer and R&D-reporter shares. The
  difference, 0.77 of accuracy, is manufactured by the ranking.

## 5. Mechanism, verified on the parquet

`dataset.md` (ADR 0008): "`percent_rank()` within (calendar quarter,
snapshot_kind) over non-NULL values … Ties share the lower percent rank."

For a tied group at value *v* in quarter *q*, every member's rank is
`(# rows with value < v in q) / (n_q − 1)`: the share of the quarter's
cross-section below the group. That share is a property of the quarter, not
of the firm, and it differs from every other quarter's. `piotroski_f` takes
ten integer values, so each quarter emits ten constants; a firm with F = 5
in 2005Q1 carries the exact value "share of 2005Q1 firms with F < 5", which
appears in no other quarter. A tree needs one split per constant to recover
the quarter.

Direct check (`dataset_v1.0/dataset.parquet`):

```sql
SELECT snapshot_kind,
       count(DISTINCT piotroski_f_rank)            AS distinct_rank_values,
       count(DISTINCT (quarter, piotroski_f_rank)) AS distinct_quarter_value_pairs,
       count(DISTINCT quarter)                     AS quarters
FROM 'dataset.parquet' WHERE piotroski_f_rank IS NOT NULL GROUP BY 1;
```

| snapshot_kind | distinct_rank_values | distinct (quarter, value) pairs | quarters |
|---|---|---|---|
| low | 1043 | 1160 | 116 |
| median | 1044 | 1160 | 116 |
| high | 1040 | 1158 | 116 |

1160 pairs over 116 quarters is ten values per quarter, one per score.
1044 = 1160 − 116: the single value shared across quarters is the bottom
group's 0.0; the other nine constants of every quarter occur in that
quarter only. The column is, to a tree, a quarter id with ten aliases.

Column classes affected, from `features.md`:

- **Integer composites** [verified for `piotroski_f_rank`; the four-column
  run puts `mohanram_g7_rank` in the same class] — worst case, every level
  is a key: `piotroski_f` (0–9), `mohanram_g7` (0–7). In v1.1's trend family also
  `fund_history_quarters`, `div_years_paid_10y`, `div_streak_10y`,
  `div_cuts_10y`, `div_history_years_10y`, and the `*_up_frac_{4,8,12,20}q`
  and `ocf_positive_frac_{w}q` shares, which take at most w+1 values.
  `conservative_score` is a rank-sum and inherits the property from its inputs.
- **Zero-inflated ratios** [inferred: `rnd_to_assets_rank` and
  `dividend_yield_rank` carry 0.44 and 0.35 of the gain importance in the
  no-technicals run, and both are in the 0.917 four-column arm, but neither
  was run alone] — the zero group ranks 0.0 everywhere (harmless), but the
  first non-zero rank equals the quarter's zero share, so the support's
  lower edge is a key. Candidates: `rnd_to_assets` (explicit
  `coalesce(rnd, 0)` fill, ADR 0013), `dividend_yield`, `net_payout_yield`,
  `capex_to_assets`, `ext_financing_to_assets`, and any other ratio whose
  numerator is commonly exactly zero. The tie-mass audit in §8 settles the
  list.
- **Sector ranks** (`_secrank`) [inferred, not measured] use the same
  construction on thinner slices (guard 20) and will carry the same keys,
  more of them.
- **Rank guard NULLs** and tier gates (`manual.md` §6) [inferred] add an
  era-dependent missingness pattern; a smaller effect that also dates the
  burn-in years.

Continuous features are, in practice, safe: their rank granularity is
1/(n_q − 1), below what histogram binning resolves.

## 6. What we ask of the next dataset version

Decisions for an ADR (our recommendation first in each case):

1. **Do not rank integer-valued composites and counts.** Ship the raw score;
   it is already cross-sectionally comparable. If a [0, 1] version is wanted,
   use a fixed scale (`piotroski_f / 9`), never a within-quarter rank. Apply
   the same rule to every count and share column in §5 and to
   `conservative_score`'s inputs, or define it from fixed-scale scores.
2. **Decide the mass-point policy explicitly.** Options, best first:
   (a) rank over the non-zero support only, with the zero group mapped to a
   fixed sentinel (0.0) and the existing sign/flag columns carrying the
   "is zero" information — the lower edge of the support then stops
   encoding the zero share; (b) keep the current construction but publish,
   per rank column, its tie mass (§6.4) so consumers can exclude columns
   above a threshold; (c) leave as is, documented as a known quarter key.
   Note that changing the tie convention (average, dense, midpoint) does
   *not* help: any deterministic function of the tied group's share is a
   key.
3. **Version it as a breaking change.** Column semantics change, so
   downstream must not compare results across the boundary
   (`data/versions.md`); rank-fed configs will need a
   `min_dataset_version` bump.
4. **Add a build-time audit and put it in the manifest.** For every rank
   column and snapshot kind: (i) tie mass = share of rows whose rank value
   is shared with ≥ 1 other row in the same (quarter, kind); (ii)
   distinct-values vs. distinct-(quarter, value)-pairs, as in §5. Fail the
   build, or at least flag the column, when tie mass exceeds a threshold
   (a few percent). Both are one aggregation over the parquet.
5. **Re-run the era probe as an acceptance test** for the new version: a
   `ranks`-only probe under `entity_holdout` should land near the raw
   four-column level (≈ 0.15), not 0.9. Downstream will run it on receipt
   (`scripts/run_diagnostic.py era-probe`); upstream can run the same
   config against the candidate build.

6. **Keep the raw columns and flags as they are.** The raw four-column
   arm's 0.148 is genuine drift in payer and R&D-reporter shares and is
   the kind of era signal a walk-forward model is entitled to see. Nothing
   here argues for changing the raw feature registry.

## 7. Implications downstream, for the record

- `walkforward` and `holdout` results published so far are not inflated by
  this mechanism. Test quarters are never in training, so the key has
  nothing to look up. Deployment scoring likewise produces fresh constants.
- They may be *understated*: a rank-fed tree spends splits memorising
  training quarters, and those splits route arbitrarily on a new quarter.
- The constants are also an implicit market-state feature (the share of
  firms below score F is a point-in-time measure of aggregate health).
  That is legitimate information, but PLAN §5.6 gates market-regime
  features behind an ablation, and ranks bring them in unannounced.
- Extracted rules on these columns read wrongly: `piotroski_f_rank > 0.41`
  is a different score cutoff in every quarter.
- The leakage-gap experiment on rank models must exclude the discrete-score
  ranks, or its entity_holdout − walkforward gap is mostly this.

## 8. Reproduction

Probe (downstream repo, branch `claude/era-identifiability-probe`):

```sh
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_rank_3y.toml
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_rank_notech_3y.toml
# four-column arms: [features] columns = [...] with the rank / raw names above
```

Entity-disjointness of the split (expected 0):

```sql
SELECT count(*) FROM (
  SELECT DISTINCT permaticker FROM 'splits.parquet'
   WHERE scheme = 'entity_holdout' AND horizon_years = 3 AND role = 'train'
  INTERSECT
  SELECT DISTINCT permaticker FROM 'splits.parquet'
   WHERE scheme = 'entity_holdout' AND horizon_years = 3 AND role = 'test');
```

Tie-mass audit, all rank columns at once (DuckDB; substitute the manifest's
`ranks` list for the two columns shown):

```sql
WITH long AS (
  SELECT quarter, snapshot_kind, name, value
  FROM (SELECT quarter, snapshot_kind, piotroski_f_rank, dividend_yield_rank
        FROM 'dataset.parquet')
  UNPIVOT (value FOR name IN (piotroski_f_rank, dividend_yield_rank))
  WHERE value IS NOT NULL
), grp AS (
  SELECT name, quarter, snapshot_kind, value, count(*) AS n
  FROM long GROUP BY ALL
)
SELECT name,
       sum(n) FILTER (WHERE n > 1) / sum(n)          AS tie_mass,
       count(DISTINCT value)                          AS distinct_values,
       count(DISTINCT (quarter, snapshot_kind, value)) AS quarter_value_pairs
FROM grp GROUP BY name ORDER BY tie_mass DESC;
```

A column with `tie_mass` near 0 and `quarter_value_pairs ≈ distinct_values`
is continuous and safe; one with large tie mass whose pairs exceed its
distinct values by roughly the number of (quarter, kind) cells is a key.

## 9. Suggested upstream task breakdown

1. **Audit** (no decision needed): run the §8 tie-mass query over every
   `ranks` and `sector_ranks` column of `dataset_v1.0`, per snapshot kind.
   Output a table `(column, tie_mass, distinct_values,
   quarter_value_pairs)`. This fixes the affected-column list and replaces
   the [inferred] items above with measurements.
2. **ADR — ranking discrete and mass-point features.** Record: the
   mechanism (§5), the audit table, the decision on integer composites
   (§6.1, recommended: do not rank; ship fixed-scale if needed), the
   decision on mass-point ratios (§6.2 options a/b/c), and the explicit
   note that changing the tie convention is not a remedy.
3. **ADR or amendment to ADR 0008 — rank audit as a build gate.** The
   tie-mass statistic per rank column goes into `manifest.json`; the build
   fails or flags above a threshold.
4. **Implement** in the rank stage: skip or re-derive the listed columns;
   apply the mass-point policy; recompute `conservative_score` from
   fixed-scale inputs if §6.1 changes its inputs.
5. **Version and document**: breaking version bump; `dataset.md` §Ranks
   and `features.md` conventions updated; a `versions.md`-style row for
   downstream stating which rank columns were removed or re-defined so
   configs can declare `min_dataset_version`.
6. **Acceptance test**: era probe on the candidate build (§6.5), plus the
   §8 disjointness query for `entity_holdout` [pending on our side].
7. **Notify downstream**: the leakage-gap experiment (decision 0010) and
   any rank-fed model comparison should be re-run on the new version; no
   cross-version comparison of results.

