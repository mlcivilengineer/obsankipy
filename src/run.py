import logging
from typing import List

from anki.manager import (
    AnkiManager,
)
from config_parser import NewConfig
from notes.manager import set_new_ids
from notes.note import NoteType
from utils.helpers import erase_note_ids_in_the_files
from utils.helpers import open_cache, write_hashes_to_file
from vault import VaultManager

logger = logging.getLogger(__name__)


def run(config: NewConfig):
    vault_name = config.vault.dir_path.name
    logger.info(f"Processing vault: {vault_name}")
    logger.info(f"Vault path: {config.vault.dir_path}")
    logger.info(f"Media path: {config.vault.medias_dir_path}")
    logger.info(f"Anki URL: {config.globals.anki.url}")
    
    # Initialize cache and note types
    hashes_path = config.hashes_cache_dir / f".{vault_name}_file_hashes.json"
    logger.debug(f"Cache file path: {hashes_path}")
    hashes = open_cache(hashes_path)
    logger.debug(f"Loaded {len(hashes)} file hashes from cache")
    
    note_types: List[NoteType] = config.get_note_types()
    logger.debug(f"Configured note types: {[nt.name for nt in note_types]}")
    
    # Connect to Anki
    logger.info("Connecting to Anki...")
    anki_requester = AnkiManager(config.globals.anki.url)

    # Get existing data from Anki
    logger.info("Retrieving existing note IDs from Anki...")
    ids = anki_requester.get_ids()
    logger.info(f"Found {len(ids)} existing notes in Anki")
    
    logger.info("Retrieving media files from Anki...")
    medias_in_anki = anki_requester.get_medias(config.globals.anki.fine_grained_image_search)
    pics_in_anki = medias_in_anki["images"]
    audios_in_anki = medias_in_anki["audios"]
    logger.info(f"Found {len(pics_in_anki)} images and {len(audios_in_anki)} audio files in Anki")

    # Initialize vault manager
    logger.info("Scanning vault for files...")
    vault = VaultManager(
        config.vault.dir_path,
        config.vault.exclude_dirs_from_scan,
        config.vault.exclude_dotted_dirs_from_scan,
        config.vault.file_patterns_to_exclude,
        note_types,
    )

    # Process files
    vault.set_new_files(hashes)
    logger.info(f"Found {len(vault.new_files)} new or modified files to process")
    if not vault.new_files:
        logger.info(f"Nothing has changed since last run")
        return

    # Extract and categorize notes
    logger.info("Extracting notes from files...")
    notes_manager = vault.get_notes_from_new_files()
    total_notes = len(notes_manager.get_all_notes())
    logger.info(f"Extracted {total_notes} notes from files")
    
    logger.info("Categorizing notes (new/existing/deleted)...")
    notes_manager.categorize_notes(ids)
    
    logger.info("Loading media data...")
    notes_manager.load_media_data(config.vault.medias_dir_path)
    
    logger.info("Categorizing media files...")
    notes_manager.categorize_medias(pics_in_anki, audios_in_anki)
    medias = notes_manager.get_media_to_add()

    # Get categorized notes
    notes_to_edit = notes_manager.get_all_notes_to_edit()
    notes_to_add = notes_manager.get_all_notes_to_add()
    notes_to_delete = notes_manager.get_all_notes_to_delete()
    decks_to_create = notes_manager.get_needed_target_decks()
    
    # Log summary of operations
    logger.info("=" * 50)
    logger.info("SYNCHRONIZATION SUMMARY:")
    logger.info(f"  Notes to add: {len(notes_to_add)}")
    logger.info(f"  Notes to edit: {len(notes_to_edit)}")
    logger.info(f"  Notes to delete: {len(notes_to_delete)}")
    logger.info(f"  Media files to add: {len(medias)}")
    if decks_to_create:
        logger.info(f"  Making sure that these Decks exist: {list(decks_to_create)}")
    logger.info("=" * 50)
    
    # Execute operations
    if decks_to_create:
        logger.info("Creating new decks...")
        anki_requester.create_decks(decks_to_create)
    
    if notes_to_delete:
        logger.info(f"Deleting {len(notes_to_delete)} notes...")
        anki_requester.delete_notes(notes_to_delete)
        logger.info("Removing note IDs from source files...")
        erase_note_ids_in_the_files([note.source_file.path for note in notes_to_delete])

    if notes_to_add:
        logger.info(f"Adding {len(notes_to_add)} new notes...")
        add_response = anki_requester.adds_new_notes(notes_to_add)

        if add_response:
            logger.info(f"Successfully added {len(add_response)} notes")
            logger.info("Updating source files with new note IDs...")
            set_new_ids(add_response)
            out_of_date_files = notes_manager.get_out_of_date_files()
            for file in out_of_date_files:
                file.write_new_ids_to_file()
            logger.info(f"Updated {len(out_of_date_files)} source files with new IDs")
        else:
            logger.warning("No notes were added (possibly all duplicates)")
    else:
        logger.info("No new notes to add")

    if notes_to_edit:
        logger.info(f"Updating {len(notes_to_edit)} existing notes...")
        anki_requester.updates_existing_notes(notes_to_edit)
        logger.info("Ensuring notes are in correct decks...")
        anki_requester.ensure_correct_deck(notes_to_edit)
    else:
        logger.info("No notes to update")

    if medias:
        logger.info(f"Uploading {len(medias)} media files...")
        anki_requester.store_media_files(medias)
    else:
        logger.info("No new media files to upload")

    # Update cache
    logger.info("Updating file hash cache...")
    curr_hashes = vault.get_curr_file_hashes()
    write_hashes_to_file(curr_hashes, hashes_path)
    logger.info(f"Updated cache with {len(curr_hashes)} file hashes")
    
    # TODO need to change the Vault manager to manage IO operations with the files inside the vault
    # TODO need to error handle when we try to add a duplicate note
    # TODO create the cli using click
    # TODO create the tests
    # TODO better annotate python type annotations, like Any
    # TODO do logging
    # TODO what if someone deletes the ids in the obsidian note? we should be able to retrieve it back by using the findCards api, searching for the front field like this: *question*
    # TODO handle when the image referenced in the obsidian note is not in the same "case" as the file in the filesystem
    # TODO inline ids so we support lists as notes
    # TODO handle the delete path better..we might delete the structure of the note, which will stop being parsed and still want to delete it..
    # The request to delete notes is coupled with the Note object, and we should decouple it. The contents of the file will also be out of date after we delete a note it
    # and we need to update the contents to account for that
    # categorize medias maybe should get one whole type instead of 2, one for images and one for audios
