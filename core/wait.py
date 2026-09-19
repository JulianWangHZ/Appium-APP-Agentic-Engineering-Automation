"""Poll-based waiting primitive.

More general than WebDriverWait + ExpectedConditions: the condition can be any
callable, including ones that raise stale element errors. Exceptions count as
"not yet" and polling continues — elements mid-animation or mid-list-refresh
make one-shot checks fail randomly with stale errors.
"""
from __future__ import annotations

import time
from collections.abc import Callable


def poll_until(
    condition: Callable[[], bool],
    timeout: float,
    interval: float = 0.5,
    message: str = "",
    swallow: tuple[type[Exception], ...] = (Exception,),
) -> None:
    """Poll until condition() is truthy; raise TimeoutError with context otherwise.

    Exceptions from condition() count as "not yet" and keep polling — stale-safe.
    """
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            if condition():
                return
            last_error = None
        except swallow as e:  # noqa: BLE001 - stale-safe by design
            last_error = e
        time.sleep(interval)
    detail = f" (last error: {last_error})" if last_error else ""
    raise TimeoutError(f"{message or 'condition not met'} within {timeout}s{detail}")
