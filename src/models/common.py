"""Shared helpers for the model wrappers.

`resolve_class_weight` is the precision knob every classifier here
exposes uniformly. The project's core strategy is extremely high
precision at the cost of recall (PLAN §2): besides `"balanced"` (recall-
friendly — it upweights the rare positive class), a bare float `w` maps
to `{True: w, False: 1.0}`. Setting `w < 1` makes false positives
relatively more expensive than missed positives, so the model only calls
a row positive in regions that are very pure — fewer picks, higher
precision. Class weights multiply into the mandatory `sample_weight_{H}y`
uniqueness weights (sklearn and LightGBM both compose them that way);
the uniqueness weights themselves are never replaced.
"""

from __future__ import annotations

from harness.errors import ConfigError


def resolve_class_weight(
    class_weight, *, extra_modes: tuple[str, ...] = ()
) -> str | dict | None:
    """Normalize a config `class_weight` into what the estimators accept.

    - ``None`` (absent in TOML): no class weighting.
    - ``"balanced"`` (plus any estimator-specific `extra_modes`, e.g.
      random forest's ``"balanced_subsample"``): passed through.
    - a positive float ``w``: ``{True: w, False: 1.0}`` — the positive
      class's errors count `w` times a negative's. ``w == 1.0`` is the
      explicit no-op (useful as a grid point next to real values, since
      TOML cannot express null in an array).
    """
    if class_weight is None:
        return None
    modes = ("balanced", *extra_modes)
    if isinstance(class_weight, str):
        if class_weight in modes:
            return class_weight
        raise ConfigError(
            f"class_weight must be one of {list(modes)}, a positive number "
            f"(positive-class weight), or absent; got {class_weight!r}"
        )
    # bool is an int subclass; a bare `true` in TOML is a config mistake
    if isinstance(class_weight, bool) or not isinstance(class_weight, (int, float)):
        raise ConfigError(
            f"class_weight must be one of {list(modes)}, a positive number "
            f"(positive-class weight), or absent; got {class_weight!r}"
        )
    w = float(class_weight)
    if not w > 0:
        raise ConfigError(f"numeric class_weight must be > 0, got {w}")
    if w == 1.0:
        return None
    return {True: w, False: 1.0}
