import time


class LatencyTracker:
    """
    Tracks full request latency + TTFT later (streaming)
    """

    def __init__(self):
        self.start_time = None
        self.first_token_time = None

    def start(self):
        self.start_time = time.time()

    def mark_first_token(self):
        if self.first_token_time is None:
            self.first_token_time = time.time()

    def total_latency_ms(self):
        if not self.start_time:
            return None
        return round((time.time() - self.start_time) * 1000, 2)

    def ttft_ms(self):
        if not self.start_time or not self.first_token_time:
            return None
        return round((self.first_token_time - self.start_time) * 1000, 2)
