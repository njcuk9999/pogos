#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple immutable classes used to define POGOS instrument modes and workflows.

These classes intentionally contain only standard-library values and small
query helpers. Runtime reduction functions remain in their owning modules.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union


@dataclass(frozen=True)
class InputFiles:
    """Parameter keys for an externally supplied input-file collection."""

    files_key: str
    path_key: str


@dataclass(frozen=True)
class InstMode:
    """Definition of one selectable observing mode."""

    name: str
    instrument: str
    label: str
    headers: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()
    enabled: bool = True
    standard_jwst: bool = True

    def header_values(self) -> Dict[str, Tuple[str, ...]]:
        """Return required header values keyed by FITS keyword."""
        return dict(self.headers)


@dataclass(frozen=True)
class ReductionLevel:
    """Definition of an ordered reduction level."""

    name: str
    allow_multiple: bool


@dataclass(frozen=True)
class RedStep:
    """Definition of one reduction implementation at one workflow level."""

    name: str
    run_key: str
    level: ReductionLevel
    supported_modes: Tuple[InstMode, ...]
    input_files: Optional[InputFiles] = None
    config_prefix: Optional[str] = None
    sub_prefixes: Tuple[str, ...] = ()
    shared_prefixes: Tuple[str, ...] = ()
    generic_run_dir: bool = True
    run_dir_key: Optional[str] = None
    required_params: Tuple[str, ...] = ()
    mode_key: Optional[str] = None

    def supports(self, mode: Union[InstMode, str]) -> bool:
        """Return whether this step supports an instrument mode."""
        mode_name = mode.name if isinstance(mode, InstMode) else mode
        return any(item.name == mode_name for item in self.supported_modes)

    def is_enabled(self, params) -> bool:
        """Return whether this step is enabled in a parameter mapping."""
        return bool(params.get(self.run_key, False))

    @property
    def parameter_prefix(self) -> str:
        """Return the primary parameter prefix owned by this step."""
        return self.config_prefix if self.config_prefix is not None else self.name
