from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Any

from app.ai.skills_runtime.errors import DependencyCycleError, DependencyResolutionError, DependencyVersionError
from app.ai.skills_runtime.loader import SkillLoader
from app.ai.skills_runtime.models import SkillPackage
from app.ai.skills_runtime.registry import SkillRegistryService


@total_ordering
@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: str = ""

    @classmethod
    def parse(cls, raw: str) -> "SemVer":
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$", raw.strip())
        if not match:
            raise ValueError(f"Invalid semantic version: {raw}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4) or "",
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        left = (self.major, self.minor, self.patch)
        right = (other.major, other.minor, other.patch)
        if left != right:
            return left < right
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        return self.prerelease < other.prerelease


@dataclass(frozen=True)
class DependencySpec:
    name: str
    optional: bool = False
    version_constraint: str | None = None

    @classmethod
    def parse(cls, raw: str) -> "DependencySpec":
        text = raw.strip()
        optional = text.endswith("?")
        if optional:
            text = text[:-1].strip()
        if "@" in text:
            name, version_constraint = text.split("@", 1)
            return cls(name=name.strip(), optional=optional, version_constraint=version_constraint.strip() or None)
        return cls(name=text, optional=optional, version_constraint=None)


class DependencyResolver:
    def __init__(self, registry: SkillRegistryService, loader: SkillLoader) -> None:
        self._registry = registry
        self._loader = loader

    def _resolve_version(self, actual: str, expected: str) -> bool:
        actual_version = SemVer.parse(actual)
        expected = expected.strip()
        operators = (
            (">=", lambda a, b: a >= b),
            ("<=", lambda a, b: a <= b),
            (">", lambda a, b: a > b),
            ("<", lambda a, b: a < b),
            ("==", lambda a, b: a == b),
            ("=", lambda a, b: a == b),
        )
        for prefix, comparator in operators:
            if expected.startswith(prefix):
                return comparator(actual_version, SemVer.parse(expected[len(prefix):].strip()))
        return actual_version == SemVer.parse(expected)

    def _collect(self, skill: SkillPackage, known_skill_ids: set[str], stack: list[str], seen: set[str]) -> list[str]:
        warnings: list[str] = []
        for raw_requirement in skill.interfaces.requires:
            spec = DependencySpec.parse(raw_requirement)
            if spec.name in stack:
                cycle = " -> ".join([*stack, spec.name])
                raise DependencyCycleError(f"Dependency cycle detected: {cycle}")

            if spec.name not in known_skill_ids:
                if spec.optional:
                    warnings.append(f"optional dependency missing: {spec.name}")
                    continue
                warnings.append(f"missing dependency: {spec.name}")
                continue

            try:
                dependency = self._loader.load(spec.name)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"failed to load dependency {spec.name}: {exc}")
                continue

            if spec.version_constraint and not self._resolve_version(dependency.version, spec.version_constraint):
                if spec.optional:
                    warnings.append(
                        f"optional dependency version mismatch: {spec.name} requires {spec.version_constraint}, found {dependency.version}"
                    )
                else:
                    raise DependencyVersionError(
                        f"dependency version mismatch: {spec.name} requires {spec.version_constraint}, found {dependency.version}"
                    )
                continue

            key = f"{dependency.name}@{dependency.version}"
            if key in seen:
                continue
            seen.add(key)
            warnings.extend(self._collect(dependency, known_skill_ids, [*stack, spec.name], seen))

        return warnings

    def resolve(self, skill: SkillPackage, known_skill_ids: set[str]) -> list[str]:
        try:
            return self._collect(skill, known_skill_ids, [skill.name], set())
        except DependencyResolutionError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise DependencyResolutionError(str(exc)) from exc
