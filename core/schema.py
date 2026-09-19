"""Minimal JSON Schema (draft 2020-12 subset) validator with no dependencies.

Supported keywords: type, required, properties, additionalProperties, enum,
pattern, minLength, maxLength, minimum, maximum, items, minItems, uniqueItems.
Any other keyword in a schema is rejected at load time so the subset stays
honest: a schema cannot silently declare a constraint this validator ignores.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SUPPORTED = {
    "$schema", "$id", "title", "description", "type", "required", "properties",
    "additionalProperties", "enum", "pattern", "minLength", "maxLength",
    "minimum", "maximum", "items", "minItems", "uniqueItems",
}
TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float),
}


class SchemaError(ValueError):
    """Raised for a malformed schema or an unsupported keyword."""


def load_schema(path: Path) -> dict[str, Any]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    _assert_supported(schema, str(path.name))
    return schema


def _assert_supported(node: Any, where: str) -> None:
    if not isinstance(node, dict):
        return
    unknown = set(node) - SUPPORTED
    if unknown:
        raise SchemaError(f"{where}: unsupported schema keyword(s): {sorted(unknown)}")
    for key, child in node.get("properties", {}).items():
        _assert_supported(child, f"{where}.{key}")
    if isinstance(node.get("items"), dict):
        _assert_supported(node["items"], f"{where}[]")
    if isinstance(node.get("additionalProperties"), dict):
        _assert_supported(node["additionalProperties"], f"{where}.*")


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Return a list of human-readable violations (empty when valid)."""
    errors: list[str] = []
    expected = schema.get("type")
    if expected is not None:
        py_type = TYPES[expected]
        ok = isinstance(instance, py_type)
        if expected in {"integer", "number"} and isinstance(instance, bool):
            ok = False
        if not ok:
            return [f"{path}: expected {expected}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']} characters")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if schema.get("uniqueItems"):
            seen = [json.dumps(item, sort_keys=True) for item in instance]
            if len(seen) != len(set(seen)):
                errors.append(f"{path}: duplicate items")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], f"{path}[{index}]"))
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate(value, properties[key], f"{path}.{key}"))
            elif extra is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(extra, dict):
                errors.extend(validate(value, extra, f"{path}.{key}"))
    return errors
