from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class SchemaError:
    path: tuple[str, ...]
    message: str


def _path_text(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else "<root>"


def _resolve_ref(schema: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return schema

    target: Any = root
    for part in ref[2:].split("/"):
        if not isinstance(target, Mapping) or part not in target:
            raise KeyError(f"Unresolvable schema reference: {ref}")
        target = target[part]
    if not isinstance(target, dict):
        raise TypeError(f"Schema reference must resolve to an object: {ref}")
    return target


def collect_schema_errors(instance: Any, schema: dict[str, Any], *, root_schema: dict[str, Any] | None = None, path: tuple[str, ...] = ()) -> list[SchemaError]:
    root = root_schema or schema
    current = _resolve_ref(schema, root)
    errors: list[SchemaError] = []

    if "anyOf" in current:
        options = current.get("anyOf")
        if isinstance(options, list):
            for option in options:
                if isinstance(option, dict) and not collect_schema_errors(instance, option, root_schema=root, path=path):
                    break
            else:
                errors.append(SchemaError(path, "must match at least one schema in anyOf"))
                return errors

    if "oneOf" in current:
        options = current.get("oneOf")
        if isinstance(options, list):
            matches = 0
            for option in options:
                if isinstance(option, dict) and not collect_schema_errors(instance, option, root_schema=root, path=path):
                    matches += 1
            if matches != 1:
                errors.append(SchemaError(path, "must match exactly one schema in oneOf"))
                return errors

    if "allOf" in current:
        options = current.get("allOf")
        if isinstance(options, list):
            for option in options:
                if isinstance(option, dict):
                    errors.extend(collect_schema_errors(instance, option, root_schema=root, path=path))

    expected_type = current.get("type")
    if expected_type is not None:
        allowed_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_type_matches(instance, typ) for typ in allowed_types if isinstance(typ, str)):
            errors.append(SchemaError(path, f"must be of type {expected_type}"))
            return errors

    if "const" in current and instance != current["const"]:
        errors.append(SchemaError(path, f"must equal {current['const']!r}"))
        return errors

    if "enum" in current:
        enum_values = current.get("enum")
        if isinstance(enum_values, list) and instance not in enum_values:
            errors.append(SchemaError(path, f"must be one of {enum_values!r}"))
            return errors

    if isinstance(instance, str):
        min_length = current.get("minLength")
        max_length = current.get("maxLength")
        pattern = current.get("pattern")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(SchemaError(path, f"must have length >= {min_length}"))
        if isinstance(max_length, int) and len(instance) > max_length:
            errors.append(SchemaError(path, f"must have length <= {max_length}"))
        if isinstance(pattern, str) and not re.match(pattern, instance):
            errors.append(SchemaError(path, f"must match pattern {pattern!r}"))

    if isinstance(instance, list):
        min_items = current.get("minItems")
        max_items = current.get("maxItems")
        unique_items = bool(current.get("uniqueItems", False))
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(SchemaError(path, f"must have at least {min_items} items"))
        if isinstance(max_items, int) and len(instance) > max_items:
            errors.append(SchemaError(path, f"must have at most {max_items} items"))
        if unique_items and len({repr(item) for item in instance}) != len(instance):
            errors.append(SchemaError(path, "must contain unique items"))
        items_schema = current.get("items")
        if isinstance(items_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(
                    collect_schema_errors(item, items_schema, root_schema=root, path=(*path, str(index)))
                )

    if isinstance(instance, dict):
        properties = current.get("properties")
        required = current.get("required", [])
        additional_properties = current.get("additionalProperties", True)

        if isinstance(required, list):
            for key in required:
                if isinstance(key, str) and key not in instance:
                    errors.append(SchemaError((*path, key), "is required"))

        if isinstance(properties, dict):
            for key, subschema in properties.items():
                if key in instance and isinstance(subschema, dict):
                    errors.extend(
                        collect_schema_errors(instance[key], subschema, root_schema=root, path=(*path, key))
                    )

        if additional_properties is False and isinstance(properties, dict):
            extra_keys = [key for key in instance if key not in properties]
            for key in extra_keys:
                errors.append(SchemaError((*path, key), "additional properties are not allowed"))

    return errors


def _type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return True