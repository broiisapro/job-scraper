import re
from typing import Optional, Tuple


def parse_salary(salary_str: str) -> Optional[Tuple[int, int]]:
    """
    Parse salary string into (min_salary, max_salary).

    Examples:
        "$80,000 - $100,000" -> (80000, 100000)
        "$120,000" -> (120000, 120000)
    """
    if not salary_str:
        return None

    numbers = re.findall(r"\d[\d,]*", salary_str)

    if not numbers:
        return None

    values = [int(n.replace(",", "")) for n in numbers]

    if len(values) == 1:
        return values[0], values[0]

    return min(values), max(values)