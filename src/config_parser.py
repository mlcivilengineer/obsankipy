import logging
from pathlib import Path
from typing import List, Optional

import os

from notes.note import NoteType, NoteVariant

logger = logging.getLogger(__name__)


from typing_extensions import Annotated
from pydantic import BaseModel, field_validator, Field, model_validator


class AnkiConfig(BaseModel):
    url: str
    deck_name: Optional[str] = "Default"
    tags: Optional[List[str]] = []
    fine_grained_image_search: Optional[bool] = False


class VaultConfig(BaseModel):
    dir_path: Path
    medias_dir_path: Path
    exclude_dirs_from_scan: List[str] = Field(default_factory=list)
    exclude_dotted_dirs_from_scan: bool = True
    file_patterns_to_exclude: List[str] = Field(default_factory=list)

    @field_validator("dir_path", "medias_dir_path")
    def validate_and_resolve_path(cls, v: Path) -> Path:
        # Accept relative paths, resolve to absolute
        resolved_path = Path(v).expanduser().resolve()
        if not resolved_path.exists():
            raise ValueError(f"⚠️ Path '{v}' does not exist. "
                             f"There might be a typo or you are probably using relative paths and running "
                             f"the code in the wrong directory relative to the path.")
        return resolved_path


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
    globals: GlobalConfig
    vault: VaultConfig
    regex: Optional[RegexConfig]
    hashes_cache_dir: Annotated[str, Field(validate_default=True)] = ""

    def get_note_types(self):
        return self.regex.get_note_types()

    @model_validator(mode="after")
    def validate_paths(self) -> "NewConfig":
        if self.hashes_cache_dir:
            if not os.path.exists(self.hashes_cache_dir):
                raise ValueError(f"Path {self.hashes_cache_dir} does not exist")
            self.hashes_cache_dir = Path(self.hashes_cache_dir)
        else:
            self.hashes_cache_dir = Path(self.vault.dir_path) / ".obsankipy"

        return self
