import hashlib


def generate_id(text: str, source: str = "", chunk_index: int = 0) -> str:
    """
    Fully deterministic ID:
    - avoids duplicates across runs
    - avoids collision across files
    """

    raw = f"{source}::{chunk_index}::{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
