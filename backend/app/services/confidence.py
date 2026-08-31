from typing import Any


TOTAL_DIMENSIONS = 4


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(
        minimum,
        min(maximum, value),
    )


def calculate_evidence_coverage(
    signals: list[dict],
) -> float:
    dimensions = {
        signal.get("dimension")
        for signal in signals
        if signal.get("dimension")
    }

    coverage = (
        len(dimensions)
        / TOTAL_DIMENSIONS
    ) * 100

    return clamp(coverage)


def average_signal_strength(
    signals: list[dict],
) -> float:
    strengths: list[float] = []

    for signal in signals:
        strength = signal.get("strength")

        if strength is None:
            continue

        try:
            strengths.append(
                float(strength)
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

    if not strengths:
        return 0.0

    return clamp(
        sum(strengths) / len(strengths)
    )


def calculate_authenticity_confidence(
    validation_results: list[dict],
) -> float:
    values: list[float] = []

    for result in validation_results:
        value = result.get(
            "authenticity_confidence"
        )

        if value is None:
            continue

        try:
            values.append(
                float(value)
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

    if not values:
        return 50.0

    return clamp(
        sum(values) / len(values)
    )


def calculate_corroboration_score(
    validation_results: list[dict],
) -> float:
    if not validation_results:
        return 0.0

    total = len(
        validation_results
    )

    corroborated = sum(
        1
        for result in validation_results
        if int(
            result.get(
                "corroboration_count",
                0,
            )
            or 0
        ) > 0
    )

    return clamp(
        (
            corroborated
            / total
        ) * 100
    )


def calculate_consistency_score(
    validation_results: list[dict],
) -> float:
    if not validation_results:
        return 0.0

    scores: list[float] = []

    for result in validation_results:
        identity_status = result.get(
            "identity_status"
        )

        # -----------------------------------------------------
        # Strong identity mismatch is a major confidence issue.
        # -----------------------------------------------------

        if identity_status == "mismatch":
            scores.append(10.0)
            continue

        contradiction = bool(
            result.get(
                "contradiction_detected",
                False,
            )
        )

        if contradiction:
            scores.append(20.0)
            continue

        checks = [
            result.get(
                "name_consistency"
            ),
            result.get(
                "date_consistency"
            ),
            result.get(
                "amount_consistency"
            ),
            result.get(
                "period_consistency"
            ),
        ]

        known_checks = [
            check
            for check in checks
            if check is not None
        ]

        if not known_checks:
            scores.append(60.0)
            continue

        passed = sum(
            1
            for check in known_checks
            if check is True
        )

        scores.append(
            (
                passed
                / len(known_checks)
            ) * 100
        )

    return clamp(
        sum(scores) / len(scores)
    )


def calculate_identity_score(
    validation_results: list[dict],
) -> float:
    if not validation_results:
        return 50.0

    scores: list[float] = []

    for result in validation_results:
        status = result.get(
            "identity_status"
        )

        if status == "matched":
            scores.append(100.0)

        elif status == "mismatch":
            scores.append(0.0)

        else:
            scores.append(50.0)

    return clamp(
        sum(scores) / len(scores)
    )


def calculate_confidence(
    *,
    signals: list[dict],
    validation_results: list[dict],
) -> dict[str, Any]:
    coverage = calculate_evidence_coverage(
        signals
    )

    signal_strength = average_signal_strength(
        signals
    )

    authenticity = calculate_authenticity_confidence(
        validation_results
    )

    corroboration = calculate_corroboration_score(
        validation_results
    )

    consistency = calculate_consistency_score(
        validation_results
    )

    identity = calculate_identity_score(
        validation_results
    )

    # Identity is now explicitly represented in confidence.
    confidence = (
        (coverage * 0.20)
        + (signal_strength * 0.20)
        + (authenticity * 0.15)
        + (corroboration * 0.15)
        + (consistency * 0.15)
        + (identity * 0.15)
    )

    confidence = round(
        clamp(confidence),
        2,
    )

    return {
        "confidence_score": confidence,
        "components": {
            "evidence_coverage": round(
                coverage,
                2,
            ),
            "signal_strength": round(
                signal_strength,
                2,
            ),
            "authenticity_confidence": round(
                authenticity,
                2,
            ),
            "corroboration": round(
                corroboration,
                2,
            ),
            "consistency": round(
                consistency,
                2,
            ),
            "identity_consistency": round(
                identity,
                2,
            ),
        },
    }