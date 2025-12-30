from typing import Dict

from .logging import logger


class ValidationError(Exception):
    """入力検証エラーを表す例外（日本語メッセージ）。"""


def format_error_json(message: str, code: int = 1) -> Dict:
    """Return a structured error object suitable for `--json` output.

    message は日本語で渡してください。
    Also emit a structured log record for observability.
    """
    payload = {"error": {"message": message, "code": code}}
    try:
        logger.error(message, extra={"error_code": code, "extra": payload})
    except Exception:
        # Logging must never interrupt error handling
        pass
    return payload


def raise_validation(msg: str):
    """Convenience helper to raise ValidationError with Japanese message and log it."""
    try:
        logger.info(msg, extra={"phase": "validation"})
    except Exception:
        pass
    raise ValidationError(msg)
