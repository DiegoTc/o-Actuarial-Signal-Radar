"""Past-only rolling statistics and explicitly stateful residual monitors."""
import math
import statistics
from datetime import date


def month_number(value):
    dt = date.fromisoformat(value)
    return dt.year * 12 + dt.month - 1


def rolling_statistics(history, current, window, minimum, full_window=True):
    """Calendar window; filter both time axes, never include the current period."""
    values = [r for r in history if r["value"] is not None
              and 0 < month_number(current["report_date"]) - month_number(r["report_date"]) <= window
              and r["availability_date"] <= current["availability_date"]]
    values.sort(key=lambda r: r["report_date"])
    numbers = [r["value"] for r in values]
    result = {"history_count": len(numbers), "rolling_count": len(numbers),
              "history_review_count": sum(bool(r["quality_flags"]) for r in values),
              "history_negative_count": sum(n < 0 for n in numbers),
              "rolling_mean": None, "rolling_median": None, "rolling_std": None,
              "rolling_mad": None, "history_status": "insufficient_history"}
    # Partial statistics are descriptive; scoring requires the configured history.
    if numbers:
        result["rolling_mean"] = statistics.mean(numbers)
        result["rolling_median"] = statistics.median(numbers)
        result["rolling_mad"] = statistics.median(abs(n - result["rolling_median"]) for n in numbers)
    if len(numbers) >= 2:
        result["rolling_std"] = statistics.stdev(numbers)  # sample SD, ddof=1
    required = max(minimum, window if full_window else minimum)
    if len(numbers) >= required:
        result["history_status"] = "ready"
    elif values and len(numbers) < min(window, month_number(current["report_date"]) - month_number(values[0]["report_date"])):
        result["history_status"] = "insufficient_history_gap"
    return result


def standardized(value, center, scale, constant=1.0):
    if center is None or scale is None:
        return None, "insufficient_history"
    if scale == 0:
        return None, "zero_scale"
    score = constant * (value - center) / scale
    if not math.isfinite(score):
        return None, "non_finite_score"
    return score, "scored"


def ewma_update(previous, value, span):
    alpha = 2.0 / (span + 1)
    return value if previous is None else alpha * value + (1 - alpha) * previous


def cusum_update(positive, negative, z_score, drift):
    return max(0.0, positive + z_score - drift), min(0.0, negative + z_score + drift)


def signal_decision(score, watch, alert, previous_run, previous_direction, persistence):
    """Escalate only consecutive moderate-or-strong deviations of the same sign."""
    if score is None:
        return "", 0, 0, "not_scored"
    direction = 1 if score > 0 else -1 if score < 0 else 0
    if abs(score) < watch:
        return "NORMAL", 0, 0, "below_watch_threshold"
    run = previous_run + 1 if direction == previous_direction else 1
    if abs(score) >= alert:
        return "ALERT", run, direction, "strong_deviation"
    if run >= persistence:
        return "ALERT", run, direction, "persistent_watch"
    return "WATCH", run, direction, "moderate_deviation"
