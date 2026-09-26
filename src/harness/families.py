"""Feature families: the registry blocks of data/features.md, made
selectable.

The upstream feature registry organizes features into families
(valuation, profitability, …). The dataset manifest carries only the
*groups* (`features` / `ranks` / `sector_ranks`), so this module is the
downstream copy of the family membership — base feature names transcribed
from data/features.md, which must stay in sync when the dataset docs are
updated from upstream.

Family membership is expressed in base feature names; the group variants
follow the ADR 0008 naming contract (`{name}_rank`, `{name}_secrank`).
Candidate names derived here are only ever *intersected with the
manifest's declared columns* (see `Dataset.select_features`), so this
never selects a column the manifest doesn't declare — the manifest stays
the sole authority on what exists, per the no-pattern-matching rule.
"""

from __future__ import annotations

from harness.errors import ConfigError

#: Manifest groups a feature selection may draw from, in manifest order.
FEATURE_GROUPS = ("features", "ranks", "sector_ranks")

#: family -> base feature names, mirroring the data/features.md sections.
FEATURE_FAMILIES: dict[str, tuple[str, ...]] = {
    "meta": (
        "fund_datekey",
        "fund_reportperiod",
        "fundamentals_age_days",
        "has_filing_183d",
        "has_filing_365d",
        "negative_equity",
        "negative_ebitda",
        "negative_ev",
    ),
    "valuation": (
        "earnings_yield",
        "ocf_yield",
        "fcf_yield",
        "sales_yield",
        "book_to_market",
        "tangible_book_to_market",
        "ebit_to_ev",
        "ebitda_to_ev",
        "dividend_yield",
        "net_payout_yield",
        "ncav_to_marketcap",
        "ev_to_marketcap",
        "magic_formula_score",  # v1.4, ADR 0020 (assembly-stage)
    ),
    "profitability": (
        "gp_to_assets",
        "roa",
        "roe",
        "ebit_to_invcap",
        "roc_greenblatt",
        "gross_margin",
        "operating_margin",
        "net_margin",
        "fcf_margin",
        "cfo_to_assets",
        "asset_turnover",
    ),
    "growth": (
        "revenue_growth_1y",
        "revenue_growth_3y",
        "epsdil_growth_1y",
        "roa_delta_1y",
        "gross_margin_delta_1y",
        "gross_margin_delta_2y",
        "asset_turnover_delta_1y",
        "asset_growth_1y",
        "share_count_growth_1y",
    ),
    "trend": tuple(
        f"{series}_{stat}_{w}q"
        for series in ("revenue", "tangibles", "ocf")
        for stat in ("trend", "consistency", "up_frac")
        for w in (4, 8, 12, 20)
    )
    + tuple(f"ocf_positive_frac_{w}q" for w in (4, 8, 12, 20))
    + (
        "fund_history_quarters",
        "div_years_paid_10y",
        "div_streak_10y",
        "div_cuts_10y",
        "div_history_years_10y",
    ),
    # v1.4, ADR 0018: each marketcap yield against the stock's own 20q
    # history — `_vs_5y_median` (ranked) and `_5y_pctile` (raw only)
    "relvalue": tuple(
        f"{yield_}_{stat}"
        for yield_ in (
            "earnings_yield",
            "ocf_yield",
            "fcf_yield",
            "sales_yield",
            "book_to_market",
            "tangible_book_to_market",
        )
        for stat in ("vs_5y_median", "5y_pctile")
    ),
    "solvency": (
        "wc_to_assets",
        "retearn_to_assets",
        "ebit_to_assets",
        "marketcap_to_liabilities",
        "equity_to_liabilities",
        "liabilities_to_assets",
        "cl_to_ca",
        "current_ratio",
        "quick_ratio",
        "cash_to_assets",
        "debt_to_equity",
        "net_debt_to_ebitda",
        "interest_coverage",
        "ffo_to_liabilities",
        "log_assets",
        "ni_change_scaled",
        "two_year_loss",
        "liab_gt_assets",
        "altman_z",
        "altman_z_dd",
        "zmijewski",
        "ohlson_o",  # v1.4, ADR 0020
    ),
    "quality": (
        "dsri",
        "gmi",
        "aqi",
        "sgi",
        "depi",
        "sgai",
        "lvgi",
        "accruals_to_assets",
        "beneish_m",
        "piotroski_f",
        "noa_to_assets",
        "ext_financing_to_assets",
        "rnd_to_assets",
        "capex_to_assets",
        "roa_variability_3y",
        "revenue_growth_variability_3y",
        "mohanram_g7",
    )
    # v1.4, ADR 0020: the nine F-score signals as flags (NULL = unknown)
    + tuple(
        f"piotroski_{signal}"
        for signal in (
            "roa_positive",
            "cfo_positive",
            "roa_up",
            "cfo_gt_ni",
            "leverage_down",
            "liquidity_up",
            "no_issuance",
            "margin_up",
            "turnover_up",
        )
    ),
    "technical": (
        "mom_12_2",
        "mom_36_12",  # v1.4, ADR 0019
        "ret_6m",
        "ret_1m",
        "max_ret_21d",  # v1.4, ADR 0019
        "vol_12m",
        "vol_36m",
        "beta_12m",  # v1.4, ADR 0019
        "dist_52w_high",
        "dist_5y_high",  # v1.4, ADR 0019
        "price_vs_5y_avg",  # v1.4, ADR 0019
        "log_marketcap",
        "dollar_volume_3m",
        "amihud_12m",
        "conservative_score",
    ),
    "classification": (
        "sector",
        "industry",
        "famaindustry",
        "scalemarketcap",
        "siccode",
    ),
}


def parse_family_ref(ref: str) -> tuple[str | None, str]:
    """Parse a family reference: `"valuation"` (all groups) or a
    group-qualified `"ranks/valuation"` (that group's variant only).
    Returns (group_or_None, family); unknown names are errors."""
    group: str | None = None
    family = ref
    if "/" in ref:
        group, _, family = ref.partition("/")
        if group not in FEATURE_GROUPS:
            raise ConfigError(
                f"family reference {ref!r}: group {group!r} is not one of "
                f"{list(FEATURE_GROUPS)}"
            )
    if family not in FEATURE_FAMILIES:
        raise ConfigError(
            f"unknown feature family {family!r}; known families: "
            f"{sorted(FEATURE_FAMILIES)}"
        )
    return group, family


def family_group_columns(family: str, group: str) -> list[str]:
    """Candidate column names of one family within one manifest group,
    per the ADR 0008 naming contract. Callers must intersect the result
    with the manifest's declared columns before using it."""
    base = FEATURE_FAMILIES[family]
    if group == "features":
        return list(base)
    if group == "ranks":
        return [f"{b}_rank" for b in base]
    if group == "sector_ranks":
        return [f"{b}_secrank" for b in base]
    raise ConfigError(
        f"group {group!r} is not one of {list(FEATURE_GROUPS)}"
    )
