import hashlib
import logging

logger = logging.getLogger(__name__)
import os
import re
from typing import List

import frontmatter

from notes.note import Note
from utils.patterns import ID_REGEX_PATTERN
from utils.helpers import string_insert, overwrite_file_safely, compute_hash


class IDFileLocation:
    """
    This class will hold the location of the ID in the file
    """

    position: int
    id: int

    def __init__(self, position, id_number):
        self.position = position
        self.id = id_number

    def get_id_string(self):
        return f"<!--ID: {self.id}-->\n"


class FileNoteMetadata:
    target_deck: str
    vault_name: str
    tags: List[str]

    def __init__(self, target_deck=None, vault_name=None, tags=None):
        self.target_deck = target_deck
        self.vault_name = vault_name
        self.tags = tags


class File:
    """
    A dir will have multiple files
    A file will have 0 or more Notes
    A file may override the default target deck
    The notes inside the file can be:
        - added (if no ID is found)
        - edited (if the ID found matches one ID in anki)
        - deleted (if there is a DELETE keyword above the ID) TODO
    """

    file_name: str
    path: str
    file_note_metadata: FileNoteMetadata
    curr_file_content: str
    content_len: int
    original_file_content: str
    line_numbers: int
    found_notes: List
    file_hash: str
    tags: List[str]
    target_deck: str
    frontmatter: dict
    to_add_notes: List[Note]
    original_hash: str
    curr_hash: str

    def __init__(self, filepath, vault_name):
        self.path = filepath
        self.file_name = os.path.basename(filepath)
        self.read_file()
        self.original_hash = compute_hash(self.original_file_content.encode("utf-8"))
        self.curr_hash = self.original_hash
        self.line_numbers = len(self.curr_file_content.split("\n"))
        self.found_notes = []
        self.tags = self.get_tags()
        self.target_deck = self.get_target_deck()
        self.file_note_metadata = FileNoteMetadata(
            target_deck=self.target_deck, vault_name=vault_name, tags=self.tags
        )
        self.to_add_notes = []

    def read_file(self) -> None:
        """
        this method will read the file content and store it in self.curr_file_content
        """
        logger.debug(f"reading file {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            self.original_file_content = f.read()
        self.curr_file_content = self.original_file_content

        post = frontmatter.load(self.path)
        self.content_len = len(self.curr_file_content)
        metadata = post.metadata
        self.frontmatter = {k.lower(): v for k, v in metadata.items()}

    def get_tags(self) -> List[str]:
        """
        this method will return the tags of the file
        """
        tags = self.frontmatter.get("tags", "")
        if isinstance(tags, list):
            return tags
        return (
            tags.split(",") if tags is not None else []
        )  # this has to be done because sometimes people put tags in the frontmatter but leave it empty

    def get_target_deck(self) -> str:
        """
        this method will return the target deck of the file
        """
        target_deck_variants = ["deck", "target deck", "target_deck"]
        for variant in target_deck_variants:
            if variant in self.frontmatter:
                return self.frontmatter[variant]
        return "Default"

    def scan_file(self, note_types: List["NoteType"]) -> List["Note"]:
        """
        this method will scan the file content for notes
        """

        for note_type in note_types:
            for regex in note_type.regexes:
                full_regex = regex + ID_REGEX_PATTERN
                regex = re.compile(full_regex, re.MULTILINE)

                for match in regex.finditer(self.curr_file_content):
                    note = Note(
                        note_match=match,
                        source_file=self,
                        target_deck=self.target_deck,
                        note_type=note_type,
                        file_note_metadata=self.file_note_metadata,
                    )
                    self.found_notes.append(note)
        logger.debug(f"found {len(self.found_notes)} notes in file {self.path}")
        return self.found_notes

    def append_to_add_notes(self, note: Note) -> None:
        """
        this method will append a note to the list of notes to add
        """
        self.to_add_notes.append(note)

    def original_hash(self) -> str:
        """
        this method will return the hash of the file
        """
        return hashlib.sha256(self.original_file_content.encode("utf-8")).hexdigest()

    def overwrite_content_with_new_ids(self, ids: List[IDFileLocation]) -> None:
        """
        this method will overwrite the file content with the new ID created by anki
        """
        curr_text = self.curr_file_content
        self.curr_file_content = string_insert(
            curr_text, [(id.position, id.get_id_string()) for id in ids]
        )

    def get_id_file_location_from_added_notes(self) -> List[IDFileLocation]:
        """
        we need to get the location of the last character of the answer, so we use group 2, which will be the answer
        """
        return [
            IDFileLocation(note.id_location_in_file, note.id)
            for note in self.to_add_notes
        ]

    def write_new_content(self) -> None:
        """
        this method will write the new content to the file
        """
        overwrite_file_safely(self.path, self.curr_file_content)

    def write_new_ids_to_file(self):
        id_locations = self.get_id_file_location_from_added_notes()
        self.overwrite_content_with_new_ids(id_locations)
        self.write_new_content()
        self.recompute_hash()

    def recompute_hash(self):
        self.curr_hash = compute_hash(self.curr_file_content.encode("utf-8"))
