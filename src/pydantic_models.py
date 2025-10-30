"""Configuration models for ObSankiPy.

- `config_path` is REQUIRED and used as the base for resolving relative paths.
- `VaultConfig` resolves its paths relative to the directory containing `config_path`.
- Cache directory defaults to `<vault.dir_path>/.obsankipy` when not set.

This module assumes `NoteType` and `NoteVariant` are defined in `notes.note`.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional
import yaml

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated

from notes.note import NoteType, NoteVariant

logger = logging.getLogger(__name__)


class AnkiConfig(BaseModel):
    """Configuration related to Anki/AnkiConnect."""

    url: str
    deck_name: Optional[str] = "Default"
    tags: Optional[List[str]] = []
    fine_grained_image_search: Optional[bool] = False


class VaultConfig(BaseModel):
    """Configuration for the Obsidian vault and media paths.

    All paths are resolved relative to the directory that contains the YAML
    configuration file (i.e., `NewConfig.config_path.parent`). Use
    :meth:`resolve_relative_paths` to perform resolution.
    """

    dir_path: Path
    medias_dir_path: Path
    exclude_dirs_from_scan: List[str] = Field(default_factory=list)
    exclude_dotted_dirs_from_scan: bool = True
    file_patterns_to_exclude: List[str] = Field(default_factory=list)

    def resolve_relative_paths(self, base_dir: Path) -> None:
        """Resolve relative paths against the provided *base_dir*.

        Parameters
        ----------
        base_dir: Path
            The directory to resolve relative paths against. Typically
            `NewConfig.config_path.parent`.
        """
        for field_name in ("dir_path", "medias_dir_path"):
            value: Path = getattr(self, field_name)
            # Allow absolute paths as-is; otherwise resolve from base_dir.
            candidate = value if value.is_absolute() else (base_dir / value)
            resolved = candidate.expanduser().resolve()
            if not resolved.exists():
                raise FileNotFoundError(
                    f"⚠️ Path '{value}' (resolved as '{resolved}') does not exist. "
                    f"Relative paths are resolved from the config directory: {base_dir}"
                )
            setattr(self, field_name, resolved)


class RegexConfig(BaseModel):
    basic: Optional[List[str]] = []
    basic_reversed: Optional[List[str]] = []
    type_answer: Optional[List[str]] = []
    cloze: Optional[List[str]] = []

    def get_note_types(self):
        note_types = []
        if self.basic:
            note_types.append(
                NoteType(
                    regexes=self.basic,
                    note_variant=NoteVariant.BASIC,
                )
            )
        if self.basic_reversed:
            note_types.append(
                NoteType(
                    regexes=self.basic_reversed,
                    note_variant=NoteVariant.BASIC_AND_REVERSED_CARD,
                )
            )
        if self.type_answer:
            note_types.append(
                NoteType(
                    regexes=self.type_answer,
                    note_variant=NoteVariant.BASIC_TYPE_ANSWER,
                )
            )
        if self.cloze:
            note_types.append(
                NoteType(
                    regexes=self.cloze,
                    note_variant=NoteVariant.CLOZE,
                )
            )
        return note_types


class GlobalConfig(BaseModel):
    anki: AnkiConfig


class NewConfig(BaseModel):
    """Top-level configuration model.

    Notes
    -----
    - `config_path` **must** point to the YAML file used to construct this model.
      It is used as the base directory for resolving all relative paths.
    - `hashes_cache_dir` defaults to `<vault.dir_path>/.obsankipy` if not provided.
    """

    config_path: Path = Field(description="Absolute path to this configuration file.")
    globals: GlobalConfig
    vault: VaultConfig
    regex: Optional[RegexConfig] = None
    hashes_cache_dir: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Path to cache dir, defaults to vault/.obsankipy",
        ),
    ]

    def get_note_types(self):
        return self.regex.get_note_types()

    @model_validator(mode="after")
    def validate_and_resolve(self) -> "NewConfig":
        # Resolve config_path first and ensure it exists
        self.config_path = self.config_path.expanduser().resolve()
        if not self.config_path.exists():
            raise FileNotFoundError(f"⚠️ Config file '{self.config_path}' does not exist.")

        base_dir = self.config_path.parent

        # Resolve vault paths relative to the config directory
        self.vault.resolve_relative_paths(base_dir)

        # Resolve hashes cache dir (relative to config dir if relative)
        if self.hashes_cache_dir is None:
            self.hashes_cache_dir = self.vault.dir_path / ".obsankipy"
        else:
            candidate = (
                self.hashes_cache_dir
                if self.hashes_cache_dir.is_absolute()
                else (base_dir / self.hashes_cache_dir)
            )
            resolved_cache = candidate.expanduser().resolve()
            if not resolved_cache.exists():
                raise FileNotFoundError(
                    f"⚠️ Cache dir '{self.hashes_cache_dir}' (resolved as '{resolved_cache}') does not exist."
                )
            self.hashes_cache_dir = resolved_cache

        logger.info("🧩 Loaded config from: %s", self.config_path)
        logger.info("📁 Vault dir: %s", self.vault.dir_path)
        logger.info("📁 Media dir: %s", self.vault.medias_dir_path)
        logger.info("📁 Cache dir: %s", self.hashes_cache_dir)
        return self


def load_config(config_file: Path) -> NewConfig:
    """Load a YAML file into `NewConfig`, auto-injecting `config_path`.

    This lets you omit `config_path` from the YAML while still requiring it
    in the model itself.
    """

    logger.info("📄 Loading configuration file...")
    config_file = config_file.expanduser().resolve()
    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    logger.info("✅ Configuration loaded successfully")
    data["config_path"] = config_file
    logger.info("🧪 Parsing and validating configuration...")
    return NewConfig(**data)
