from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FabCardVaultError(Exception):
    error_type: str
    message: str
    details: dict[str, object] = field(default_factory=dict)

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "type": self.error_type,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return {"error": payload}

    def __str__(self) -> str:
        return self.message


class NotFoundError(FabCardVaultError):
    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__("not_found", message, details or {})


class InvalidPageError(FabCardVaultError):
    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__("invalid_page", message, details or {})


class UpstreamError(FabCardVaultError):
    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__("upstream_error", message, details or {})
