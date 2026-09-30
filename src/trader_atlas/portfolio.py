"""Portfolio sizing primitives shared by research and paper decisions."""

from __future__ import annotations

import math


def volatility_target_weight(
    *,
    target_annual_volatility: float,
    estimated_annual_volatility: float,
    maximum_weight: float,
) -> float:
    """Return a bounded long-only risk-asset weight.

    Invalid or non-positive volatility estimates fail to cash. This makes the
    conservative behavior explicit and independently testable.
    """

    if not math.isfinite(estimated_annual_volatility) or estimated_annual_volatility <= 0.0:
        return 0.0
    raw = target_annual_volatility / estimated_annual_volatility
    return min(maximum_weight, max(0.0, raw))
