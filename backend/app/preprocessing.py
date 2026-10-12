MAX_DELIVERIES = 8
MAX_TEXT_LENGTH = 300


def clean_text(text: str) -> str:
    """Trim the ends and collapse repeated whitespace into one space."""
    return " ".join(text.split())


def clean_lines(raw: str) -> list[str]:
    """Split text into lines, clean each one and drop blank lines."""
    lines = [clean_text(line) for line in raw.splitlines()]
    return [line for line in lines if line]


def validate_lines(lines: list[str]) -> None:
    """Raise ValueError when the number or length of deliveries is not allowed."""
    if not lines:
        raise ValueError("Enter at least one delivery address.")
    if len(lines) > MAX_DELIVERIES:
        raise ValueError(f"A maximum of {MAX_DELIVERIES} deliveries is supported.")
    for line in lines:
        if len(line) > MAX_TEXT_LENGTH:
            raise ValueError(f"Each delivery must be {MAX_TEXT_LENGTH} characters or fewer.")
