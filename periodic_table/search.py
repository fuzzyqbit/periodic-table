from periodic_table.model import Element


def match(query: str, element: Element) -> bool:
    q = query.strip()
    if not q:
        return True
    q_lower = q.lower()
    if element.symbol.lower() == q_lower:
        return True
    if element.name.lower().startswith(q_lower):
        return True
    try:
        if int(q) == element.atomic_number:
            return True
    except ValueError:
        pass
    return False
