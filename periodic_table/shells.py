_CAPACITIES = (2, 8, 18, 32, 32, 18, 8)


def fill_shells(z: int) -> list[int]:
    if z < 1:
        raise ValueError("atomic number must be >= 1")
    remaining = z
    result: list[int] = []
    for cap in _CAPACITIES:
        if remaining == 0:
            break
        n = min(cap, remaining)
        result.append(n)
        remaining -= n
    if remaining > 0:
        raise ValueError(f"atomic number {z} exceeds supported shell capacity")
    return result
