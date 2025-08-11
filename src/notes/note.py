import enum
from typing import List, Optional, Any

from notes.fields import NoteField, FrontField, BackField
from media import Picture, Audio
from utils.patterns import (
    IMAGE_FILE_WIKILINK_REGEX,
    AUDIO_FILE_REGEX,
    IMAGE_FILE_MARKDOWN_REGEX,
)

from urllib.parse import unquote


class State(enum.Enum):
    EXISTING = enum.auto()
    UNKNOWN = enum.auto()
    NEW = enum.auto()
    MARKED_FOR_DELETION = enum.auto()


# interface of Field using Protocol


class DuplicateScopeOptions:
    deck_name: str
    check_children: bool
    check_all_models: bool


class NoteOptions:
    allow_duplicate: bool
    duplicate_scope: str
    duplicate_scope_options: DuplicateScopeOptions


class Note:
    state: State
    note_type: Any
    note_id: int | None
    cards_ids: list[int] | None
    source_file: "File"
    note_start_span: int
    note_end_span: int
    original_note_text: str
    target_deck: str
    tags: List[str]
    fields: List[NoteField]  # implements the interface of NoteField
    medias: List[Any]
    to_delete: bool
    options: NoteOptions
    file_note_metadata: "FileNoteMetadata"
    id_location_in_file: int

    def __init__(
        self,
        note_match,
        source_file,
        target_deck,
        note_type,
        file_note_metadata,
    ):
        """
        based on the match, source file, target deck and note type
        we should get all the other attributes
        """
        self.note_type = note_type
        self.note_match = note_match
        self.file_note_metadata = file_note_metadata
        self.original_note_text = note_match.group(0)

        named_captures = note_match.groupdict()
        self.check_state(named_captures)

        self.source_file = source_file
        self.note_start_span = note_match.start()
        self.note_end_span = note_match.end()
        self.curr_note_text = self.original_note_text
        self.target_deck = target_deck
        self.tags = ["Obsidian"] + self.file_note_metadata.tags

        self.medias = list()
        self.audios = list()
        self.find_medias()
        self.create_fields()
        self.set_id_location_in_file()

        self.options = NoteOptions()
        self.cards_ids = None

    def check_state(self, named_captures):
        if named_captures["delete"] is not None:
            self.state = State.MARKED_FOR_DELETION
            self.note_id = int(named_captures["id_num"])
        elif named_captures["id_num"] is not None:
            self.state = (
                State.UNKNOWN
            )  # this id may exist in anki, we need to check later
            self.note_id = int(named_captures["id_num"])
        else:
            self.state = State.NEW
            self.note_id = None

    def set_id_location_in_file(self):
        if self.note_type.note_type == NoteVariant.CLOZE:
            self.id_location_in_file = self.note_match.end(
                1
            )  # because there is no back field
        else:
            self.id_location_in_file = self.note_match.end(2)

    def find_medias(self):
        for match in IMAGE_FILE_WIKILINK_REGEX.finditer(self.original_note_text):
            full_file_name = f"{match.group('filename')}.{match.group('extension')}"
            pic = Picture(filename=full_file_name)
            self.medias.append(pic)
        for match in IMAGE_FILE_MARKDOWN_REGEX.finditer(self.original_note_text):
            full_file_name = unquote(
                f"{match.group('filename')}.{match.group('extension')}"
            )
            pic = Picture(filename=full_file_name)
            self.medias.append(pic)
        for match in AUDIO_FILE_REGEX.finditer(self.original_note_text):
            full_file_name = f"{match.group('filename')}.{match.group('extension')}"
            audio = Audio(filename=full_file_name)
            self.medias.append(audio)

    def set_state(self, state):
        self.state = state

    def create_fields(self):
        if (
            self.note_type.note_type == NoteVariant.BASIC
            or self.note_type.note_type == NoteVariant.BASIC_AND_REVERSED_CARD
            or self.note_type.note_type == NoteVariant.BASIC_TYPE_ANSWER
        ):
            vault_name = self.source_file.file_note_metadata.vault_name
            file_name = self.source_file.file_name
            self.fields = [
                FrontField(self.note_match.group(1), vault_name, file_name),
                BackField(self.note_match.group(2), vault_name),
            ]
        elif self.note_type.note_type == NoteVariant.CLOZE:
            vault_name = self.source_file.file_note_metadata.vault_name
            file_name = self.source_file.file_name
            # use the FrontField because the transformations will be the same, just change the field name
            self.fields = [
                FrontField(
                    self.note_match.group(1), vault_name, file_name, field_name="Text"
                )
            ]

        for field in self.fields:
            field.transform()

    def to_anki_dict(self):
        if self.state == State.NEW:  # to be used with addNote in anki
            return {
                "modelName": self.note_type.to_anki_dict(),
                "deckName": self.target_deck,
                "tags": self.tags,
                "fields": {
                    field.get_field_name(): field.get_field_value()
                    for field in self.fields
                },
            }
        else:  # to be used with updateNote in anki
            return {
                "id": self.note_id,
                "modelName": self.note_type.to_anki_dict(),
                "deckName": self.target_deck,
                "tags": self.tags,
                "fields": {
                    field.get_field_name(): field.get_field_value()
                    for field in self.fields
                },
            }


class NoteVariant(enum.Enum):
    BASIC = enum.auto()
    CLOZE = enum.auto()
    BASIC_AND_REVERSED_CARD = enum.auto()
    BASIC_TYPE_ANSWER = enum.auto()

    def get_string(self):
        if self == NoteVariant.BASIC:
            return "Basic"
        elif self == NoteVariant.CLOZE:
            return "Cloze"
        elif self == NoteVariant.BASIC_AND_REVERSED_CARD:
            return "Basic (and reversed card)"
        elif self == NoteVariant.BASIC_TYPE_ANSWER:
            return "Basic (type in the answer)"


class NoteType:
    name: str
    regexes: List[str]

    def __init__(self, note_variant: NoteVariant, regexes: List[str]):
        self.note_type = note_variant
        self.name = note_variant.get_string()
        self.regexes = regexes

    def to_anki_dict(self):
        return self.name

    def __str__(self):
        return f"{self.name} with the regexes: {self.regexes}"
