from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

_SUPPRESS = [HealthCheck.too_slow]

settings.register_profile(
    "default",
    settings(max_examples=100, deadline=None, suppress_health_check=_SUPPRESS),
)
settings.register_profile(
    "ci",
    settings(max_examples=150, deadline=None, suppress_health_check=_SUPPRESS),
)
settings.register_profile(
    "fuzz",
    settings(max_examples=500, deadline=None, suppress_health_check=_SUPPRESS),
)

settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))
