import os
from pathlib import Path

from files import File
from notes.note import NoteType
from notes.manager import NotesManager
from utils.helpers import get_files_paths

import logging

logger = logging.getLogger(__name__)


class VaultManager:
    """
    responsible for managing the vault files, doing IO operations and getting the notes from the files
    """

    vault_name: str
    dir: Path
    file_paths: list[Path]
    files: list[File]
    new_files: list[File]
    exclude_dirs: list[str]
    exclude_dotted_dirs: bool
    note_types: list[NoteType]

    def __init__(
        self,
        vault_path: Path,
        exclude_dirs=None,
        exclude_dotted_dirs=True,
        patterns_to_exclude=None,
        note_types=None,
    ):
        self.dir = vault_path
        self.vault_name = os.path.basename(self.dir)
        logger.info(f"Vault name: {self.vault_name}")
        self.file_paths = get_files_paths(
            self.dir,
            exclude_dirs=exclude_dirs,
            exclude_dotted_dirs=exclude_dotted_dirs,
            patterns_to_exclude=patterns_to_exclude,
        )
        logger.debug(f"Files found: {self.file_paths}")
        self.set_files()
        self.note_types = note_types

    def set_new_files(self, file_hashes):
        self.new_files = [
            file for file in self.files if file.original_hash not in file_hashes
        ]

    def set_files(self):
        self.files = [
            File(file, vault_name=self.vault_name) for file in self.file_paths
        ]

    def get_notes_from_new_files(self) -> NotesManager:
        """Scan all the new files found in vault."""

        notes = []
        for file in self.new_files:
            curr_notes = file.scan_file(note_types=self.note_types)
            notes.extend(curr_notes)
        return NotesManager(notes)

    def get_curr_file_hashes(self):
        return [file.curr_hash for file in self.files]
