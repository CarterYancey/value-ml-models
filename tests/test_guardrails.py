"""The guardrails must raise — sealed holdout, diagnostic schemes,
fitting without the horizon's sample weight."""

import numpy as np
import pandas as pd
import pytest

from harness.dataset import Dataset, SplitAccess
from harness.errors import (
    DiagnosticSchemeError,
    HoldoutAccessError,
    MissingSampleWeightError,
    SplitApplicationError,
)
from models.baselines import (
    MajorityClassBaseline,
    RandomRankingBaseline,
    RankFactorBaseline,
)


@pytest.fixture(scope="module")
def ds(dataset_dir):
    return Dataset(dataset_dir)


def test_holdout_sealed_by_default(ds):
    with pytest.raises(HoldoutAccessError):
        ds.apply_split("holdout", 2018, 3)


def test_holdout_open_to_final_eval_only(ds):
    split = ds.apply_split("holdout", 2018, 3, access=SplitAccess.FINAL_EVAL)
    assert len(split.test) > 0
    with pytest.raises(HoldoutAccessError):
        ds.apply_split(
            "holdout", 2018, 3, access=SplitAccess.REGISTERED_DIAGNOSTIC
        )


@pytest.mark.parametrize("scheme", ["entity_holdout", "random_kfold"])
def test_diagnostic_schemes_refused_by_default(ds, scheme):
    with pytest.raises(DiagnosticSchemeError):
        ds.apply_split(scheme, 0, 3)
    with pytest.raises(DiagnosticSchemeError):
        ds.apply_split(scheme, 0, 3, access=SplitAccess.FINAL_EVAL)


@pytest.mark.parametrize("scheme", ["entity_holdout", "random_kfold"])
def test_diagnostic_schemes_open_to_registered_runner(ds, scheme):
    split = ds.apply_split(
        scheme, 0, 3, access=SplitAccess.REGISTERED_DIAGNOSTIC
    )
    assert len(split.train) > 0 and len(split.test) > 0


def test_unknown_scheme_refused(ds):
    with pytest.raises(SplitApplicationError, match="unknown split scheme"):
        ds.apply_split("train_test_split", 0, 3)


@pytest.mark.parametrize(
    "model",
    [
        MajorityClassBaseline(),
        RankFactorBaseline("book_to_market_rank"),
        RandomRankingBaseline(seed=1),
    ],
)
def test_fit_without_sample_weight_refused(model):
    X = pd.DataFrame({"book_to_market_rank": [0.1, 0.9]})
    y = np.array([0, 1])
    with pytest.raises(MissingSampleWeightError):
        model.fit(X, y)  # no sample_weight
    with pytest.raises(MissingSampleWeightError):
        model.fit(X, y, sample_weight=np.array([0.5, np.nan]))


def test_fit_data_requires_horizon_weight_column(ds):
    split = ds.apply_split("walkforward", 2016, 3)
    with pytest.raises(MissingSampleWeightError):
        # horizon 1 has no split tags here, but the weight-column check is
        # what we exercise: drop the column from the manifest view
        ds.manifest["columns"]["sample_weights"].remove("sample_weight_1y")
        try:
            ds.sample_weight_column(1)
        finally:
            ds.manifest["columns"]["sample_weights"].insert(
                0, "sample_weight_1y"
            )
    # the 3y weight is present and the fit assembles
    fit = ds.fit_data(
        split.train, "label_3y_beat_spy", ["book_to_market_rank"], 3
    )
    assert fit.effective_size == pytest.approx(fit.sample_weight.sum())
    assert not np.isnan(fit.sample_weight).any()
