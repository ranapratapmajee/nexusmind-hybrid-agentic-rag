import time


class LatencyTracker:
    """
    Tracks:
    - Total latency
    - Time To First Token (TTFT)

    RULES:
    - No prints
    - No streaming
    - Orchestrator controls usage
    """

    def __init__(self):
        self.start_time = None
        self.first_token_time = None

    # -------------------------
    # START REQUEST
    # -------------------------
    def start(self):
        self.start_time = time.time()

    # -------------------------
    # MARK FIRST TOKEN
    # -------------------------
    def mark_first_token(self):
        if self.first_token_time is None:
            self.first_token_time = time.time()

    # -------------------------
    # TOTAL LATENCY
    # -------------------------
    def total_latency_ms(self):
        if self.start_time is None:
            return None
        return round((time.time() - self.start_time) * 1000, 2)

    # -------------------------
    # TIME TO FIRST TOKEN
    # -------------------------
    def ttft_ms(self):
        if self.start_time is None or self.first_token_time is None:
            return None
        return round((self.first_token_time - self.start_time) * 1000, 2)

    # -------------------------
    # EXPORT SUMMARY
    # -------------------------
    def summary(self):
        return {
            "total_latency_ms": self.total_latency_ms(),
            "ttft_ms": self.ttft_ms(),
        }
