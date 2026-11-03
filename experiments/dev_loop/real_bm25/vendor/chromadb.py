"""Storage seam only: project tests replace PersistentClient; ranking is real."""


def PersistentClient(*args, **kwargs):
    raise RuntimeError("Real Chroma storage is unavailable in this offline comparison")
