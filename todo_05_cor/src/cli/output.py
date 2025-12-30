def success(text: str) -> str:
    return f"[OK] {text}"


def error(text: str) -> str:
    return f"[ERROR] {text}"


def info(text: str) -> str:
    return f"{text}"


def line(text: str) -> str:
    return text
