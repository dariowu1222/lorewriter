"""Pydantic schemas for the minimal web UI contract."""

from __future__ import annotations

from pydantic import BaseModel, Field


FieldDefault = str | int | bool | None


class TabInfo(BaseModel):
    """One frontend tab exposed by the UI contract."""

    id: str
    label: str
    mode: str
    description: str
    enabled: bool


class FieldInfo(BaseModel):
    """One input field exposed by the UI contract."""

    id: str
    label: str
    type: str
    required: bool
    default: FieldDefault = None
    placeholder: str | None = None
    help_text: str | None = None
    options: list[str] | None = None


class ActionInfo(BaseModel):
    """One action exposed by the UI contract."""

    id: str
    label: str
    description: str
    requires: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class UIContract(BaseModel):
    """Versioned frontend contract for tabs, fields, and actions."""

    version: str
    tabs: list[TabInfo]
    shared_fields: list[FieldInfo]
    manual_fields: list[FieldInfo]
    openai_fields: list[FieldInfo]
    shared_actions: list[ActionInfo]
    manual_actions: list[ActionInfo]
    openai_actions: list[ActionInfo]
