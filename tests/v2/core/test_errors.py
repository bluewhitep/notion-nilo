import json

from nilo.core.errors import (
    ConfigNotFoundError,
    CoreError,
    NotionAuthError,
    NotionOperationError,
)


def test_core_error_serializes_stable_shape() -> None:
    error = CoreError(
        message="Something failed",
        code="example_failed",
        details={"target": "page"},
    )

    assert error.to_dict() == {
        "type": "CoreError",
        "code": "example_failed",
        "message": "Something failed",
        "details": {"target": "page"},
    }


def test_specialized_errors_keep_codes() -> None:
    assert ConfigNotFoundError("/tmp/missing.json").to_dict()["code"] == "config_not_found"
    assert NotionAuthError("Invalid token").to_dict()["code"] == "notion_auth_failed"
    assert (
        NotionOperationError("pages.retrieve", "failed").to_dict()["code"]
        == "notion_operation_failed"
    )


def test_core_error_details_are_always_json_serializable() -> None:
    payload = CoreError(
        "Invalid value",
        details={"errors": [{"context": ValueError("bad value")}]},
    ).to_dict()

    assert json.loads(json.dumps(payload))["details"] == {
        "errors": [{"context": "bad value"}]
    }
