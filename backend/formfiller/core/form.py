"""
Form specification types.

A form is described at two levels:
  - The raw FIELD_MAP: one entry per PDF widget, using the PDF's own option
    codes ("/0", "/1", checkbox "/1"...). This is what gets written to the PDF.
  - Logical fields: what the LLM and the UI see. Option codes are replaced by
    readable enum values, every enum gets a "not_mentioned" escape hatch,
    mutually-exclusive checkbox sets collapse into a single enum, and fields
    that come from the user's profile (names, initials, signature block) are
    excluded from extraction entirely.

core/codec.py translates between the two.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal

NOT_MENTIONED = "not_mentioned"

FieldKind = Literal["enum", "bool", "text", "year", "number"]


@dataclass(frozen=True)
class EnumOption:
    value: str        # what the model emits, e.g. "severe_limitations"
    label: str        # human label shown in prompts and the UI
    raw: str          # PDF-level value: radio code "/2", choice text, or checkbox key


@dataclass(frozen=True)
class LogicalField:
    key: str
    section: str
    kind: FieldKind
    description: str
    options: tuple[EnumOption, ...] = ()
    mandatory: bool = False
    # For exclusive checkbox groups: the raw checkbox keys this field expands to.
    members: tuple[str, ...] = ()

    @property
    def enum_values(self) -> list[str]:
        return [o.value for o in self.options] + [NOT_MENTIONED]

    def empty_value(self):
        if self.kind == "enum":
            return NOT_MENTIONED
        if self.kind == "bool":
            return False
        return ""


@dataclass(frozen=True)
class Chunk:
    """One LLM call's worth of fields. Big sections are split into several."""
    id: str
    section: str
    keys: tuple[str, ...]


@dataclass(frozen=True)
class Section:
    id: str
    label: str
    description: str  # used by the section router prompt


@dataclass
class Issue:
    field: str | None
    severity: Literal["error", "warning", "info"]
    message: str
    rule: str

    def to_dict(self) -> dict:
        return {"field": self.field, "severity": self.severity, "message": self.message, "rule": self.rule}


@dataclass
class FormSpec:
    id: str
    title: str
    template_path: Path
    field_map: dict[str, dict]
    sections: list[Section]
    fields: dict[str, LogicalField]
    chunks: list[Chunk]
    # Profile fields: filled from user/practitioner info, never extracted.
    profile_fields: dict[str, str]                  # profile attribute -> description
    rules: Callable[[dict], list[Issue]] = lambda values: []
    # Turns (logical values + profile) into raw FIELD_MAP values that come from
    # the profile: patient name on every page, practitioner initials, etc.
    stamp_profile: Callable[[dict, dict], dict] = lambda values, profile: {}
    domain_context: str = ""
    extra: dict = field(default_factory=dict)

    def section_fields(self, section_id: str) -> list[LogicalField]:
        return [f for f in self.fields.values() if f.section == section_id]

    def chunks_for(self, section_id: str) -> list[Chunk]:
        return [c for c in self.chunks if c.section == section_id]

    def empty_values(self) -> dict:
        return {k: f.empty_value() for k, f in self.fields.items()}


# ── Helpers for building logical fields from a FIELD_MAP ─────────────────────

def slugify(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def short_enum_value(label: str) -> str:
    """'Yes - meets criteria (...)' -> 'yes'; 'normal: 0-25dB' -> 'normal'."""
    head = re.split(r"\s+[-–]\s+|:|\(", label, maxsplit=1)[0]
    return slugify(head)


def enum_options(pairs: list[tuple[str, str]]) -> tuple[EnumOption, ...]:
    """pairs of (raw, label). Uses short values unless they would collide."""
    shorts = [short_enum_value(label) for _, label in pairs]
    use_short = len(set(shorts)) == len(shorts) and all(shorts)
    return tuple(
        EnumOption(value=s if use_short else slugify(label), label=label, raw=raw)
        for (raw, label), s in zip(pairs, shorts)
    )


def infer_text_kind(key: str, description: str) -> FieldKind:
    if "year" in key and "years" not in key:
        return "year"
    if key.endswith(("_per_week",)):
        return "number"
    return "text"
