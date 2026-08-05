from dataclasses import dataclass


@dataclass
class ConfidenceDecision:
    confidence: float
    approved: bool
    retry: bool
    status: str


class ConfidencePolicy:
    """
    Determines whether the workflow should
    approve, retry, or reject based on
    the reflection confidence score.
    """

    APPROVE_THRESHOLD = 0.90
    REVIEW_THRESHOLD = 0.70

    # =====================================================
    # Evaluate Confidence
    # =====================================================

    def evaluate(
        self,
        confidence: float,
    ) -> ConfidenceDecision:

        if confidence >= self.APPROVE_THRESHOLD:

            return ConfidenceDecision(
                confidence=confidence,
                approved=True,
                retry=False,
                status="approved"
            )

        if confidence >= self.REVIEW_THRESHOLD:

            return ConfidenceDecision(
                confidence=confidence,
                approved=True,
                retry=False,
                status="approved_with_warning"
            )

        return ConfidenceDecision(
            confidence=confidence,
            approved=False,
            retry=True,
            status="retry"
        )


confidence_policy = ConfidencePolicy()