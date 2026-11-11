"""Captured contracts must fail closed when isolation is missing."""

import json
from pathlib import Path

import pytest

from quill.codex.capabilities import choose_model, validate_schema_manifest
from quill.core.errors import DomainError
from quill.core.models import ModelCapability

pytestmark = pytest.mark.unit
SCHEMA = Path(__file__).resolve().parents[2] / "schemas/codex/0.167.1/manifest.json"


def test_supported_manifest() -> None:
    validate_schema_manifest(SCHEMA)


def test_unapproved_beta_contract_rejected(tmp_path: Path) -> None:
    import shutil

    capture = tmp_path / "capture"
    shutil.copytree(SCHEMA.parent, capture)
    manifest = capture / "manifest.json"
    value = json.loads(manifest.read_text())
    value["beta_contract"] = {"approved": False}
    manifest.write_text(json.dumps(value))
    with pytest.raises(DomainError):
        validate_schema_manifest(manifest)


def test_manifest_hash_tampering_blocks(tmp_path: Path) -> None:
    value = json.loads(SCHEMA.read_text())
    value["files"] = {"ClientRequest.json": "0" * 64}
    (tmp_path / "ClientRequest.json").write_text("{}")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(value))
    with pytest.raises(DomainError, match="hash"):
        validate_schema_manifest(manifest)


def test_missing_required_method_blocks(tmp_path: Path) -> None:
    value = json.loads(SCHEMA.read_text())
    value["files"] = {}
    value["supported_methods"] = []
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(value))
    with pytest.raises(DomainError):
        validate_schema_manifest(manifest)


def test_model_missing_low_blocks() -> None:
    with pytest.raises(DomainError):
        choose_model(
            (ModelCapability(id="fixture-sol", display_name="Sol", efforts=("medium",)),), None
        )


def test_multiple_sol_requires_selection() -> None:
    catalog = tuple(
        ModelCapability(id=f"fixture-sol-{i}", display_name="Sol", efforts=("low",))
        for i in range(2)
    )
    with pytest.raises(DomainError):
        choose_model(catalog, None)
    assert choose_model(catalog, "fixture-sol-1") == catalog[1]


def test_one_available_sol_selected() -> None:
    model = ModelCapability(id="fixture-sol", display_name="Sol", efforts=("low",))
    assert choose_model((model,), None) == model


def test_unsupported_version_blocks(tmp_path: Path) -> None:
    value = json.loads(SCHEMA.read_text())
    value["cli_version"] = "unknown"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(value))
    with pytest.raises(DomainError):
        validate_schema_manifest(manifest)


def test_unrelated_display_name_not_treated_as_sol() -> None:
    with pytest.raises(DomainError):
        choose_model((ModelCapability(id="other", display_name="Console", efforts=("low",)),), None)


def test_schema_path_escape_rejected(tmp_path: Path) -> None:
    value = json.loads(SCHEMA.read_text())
    value["files"] = {"../outside.json": "0" * 64}
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(value))
    with pytest.raises(DomainError, match="fora do diretório"):
        validate_schema_manifest(manifest)


def test_catalog_parser_rejects_wrong_shape() -> None:
    from quill.codex.capabilities import parse_catalog

    with pytest.raises(DomainError):
        parse_catalog({"data": [{"id": 42}]})


def test_catalog_parser_preserves_efforts() -> None:
    from quill.codex.capabilities import parse_catalog

    models = parse_catalog(
        {
            "data": [
                {
                    "model": "fixture-sol",
                    "displayName": "Fixture Sol",
                    "supportedReasoningEfforts": [{"reasoningEffort": "low"}],
                }
            ]
        }
    )
    assert models == (
        ModelCapability(id="fixture-sol", display_name="Fixture Sol", efforts=("low",)),
    )
