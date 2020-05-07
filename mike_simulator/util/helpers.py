def clamp(min_x: float, max_x: float, x: float) -> float:
    """Restrict x to the range [min_x, max_x]"""
    return min(max(min_x, x), max_x)


def lerp(min_x: float, max_x: float, normalized_t: float) -> float:
    """Linear interpolation between min_x and max_x with normalized_t in [0, 1]"""
    return min_x + (max_x - min_x) * normalized_t
