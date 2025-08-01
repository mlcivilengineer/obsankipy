import json
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional, Union

import requests

from anki.requests import (
    AnkiGetMediaFilesNamesRequest,
    AnkiRetrieveMediaFileRequest,
    AnkiMultiRequest,
    AnkiStoreMediaFileRequest,
    AnkiAddNotesRequest,
    AnkiUpdateNoteRequest,
    AnkiFindNotesRequest,
    AnkiChangeDeckRequest,
    AnkiDeleteNotesRequest,
    AnkiCreateDeckRequest,
)
from anki.utils import _create_multi_request, _parse, T
from media import Picture
from notes.note import Note
from utils.constants import SUPPORTED_IMAGE_EXTS, SUPPORTED_AUDIO_EXTS

logger = logging.getLogger(__name__)


class AnkiManager:
    """
    This class will handle all the requests to anki
    """

    def __init__(self, url: str) -> None:
        self.url = url
        logger.debug(f"Initializing AnkiManager with URL: {url}")

    def _invoke_request(self, request: T) -> Any:
        """Do the action with the specified parameters."""
        payload = json.dumps(request.to_anki_dict()).encode("utf-8")
        response = requests.post(self.url, data=payload)
        logger.debug(
            f"sending a request to anki with the following payload: {payload} to the following url: {self.url}"
        )
        # multi response will return a result list containing multiple results, we should parse them all
        if isinstance(request, AnkiMultiRequest):
            return [_parse(r) for r in _parse(response)]
        return _parse(response)

    def get_ids(self) -> Set[int]:
        """Get a set of the currently used card IDs."""
        logger.debug("Get a set of the currently used card IDs.")
        requestJson = AnkiFindNotesRequest()
        response = self._invoke_request(requestJson)
        response = set(response)
        logger.debug(f"found the following ids in anki: {response}")
        return response

    def get_medias(self, fine_grained_search=False) -> Union[Dict[str, Dict[str, str]], Dict[str, Dict[str, Set[str]]]]:
        """get a dictionary of the media files and their data stored in anki"""
        media_file_names = self._invoke_request(AnkiGetMediaFilesNamesRequest())
        if fine_grained_search:
            media_file_multi_request = _create_multi_request(
                media_file_names, AnkiRetrieveMediaFileRequest
            )
            result = self._invoke_request(media_file_multi_request)
            result_dict = defaultdict(dict)
            for filename, data in zip(media_file_names, result):
                if filename.endswith(tuple(SUPPORTED_IMAGE_EXTS)):
                    result_dict["images"][filename] = data
                elif filename.endswith(tuple(SUPPORTED_AUDIO_EXTS)):
                    result_dict["audios"][filename] = data
            return result_dict
        else:
            result_dict = defaultdict(set)
            for filename in media_file_names:
                if filename.endswith(tuple(SUPPORTED_IMAGE_EXTS)):
                    result_dict["images"].add(filename)
                elif filename.endswith(tuple(SUPPORTED_AUDIO_EXTS)):
                    result_dict["audios"].add(filename)
            return result_dict


    def store_media_files(self, pictures: List[Picture]) -> None:
        logger.info(f"Uploading {len(pictures)} media files...")
        if not pictures:
            return
        requests = [AnkiStoreMediaFileRequest(pic) for pic in pictures]
        multi_request = AnkiMultiRequest(requests)
        response = self._invoke_request(multi_request)
        logger.debug(f"stored the following media files in anki: {response}")

    def adds_new_notes(self, notes: List[Note]) -> Optional[List[Tuple[Note, int]]]:
        """
        here we don't need to use multi, there is already a route to add multiple notes
        we need to return a list of ids of the notes that were added in the form of IDsFileLocation
        """
        logger.info(f"Adding {len(notes)} new notes to Anki...")
        if not notes:
            logger.info("No notes to add")
            return
        
        try:
            adds_new_notes_request = AnkiAddNotesRequest(notes)
            response = self._invoke_request(adds_new_notes_request)
            add_response = list(zip(notes, response))
            add_response_no_duplicates = []
            duplicates_count = 0
            
            if add_response is not None:
                # remove from add_response if the id is None, because that means it was a duplicate
                # Anki checks for uniqueness by looking at the front field, which has to be unique
                for response in add_response:
                    if response[1] is not None:
                        add_response_no_duplicates.append(response)
                    else:
                        duplicates_count += 1
                        note = response[0]
                        front = note.fields[0]
                        logger.warning(
                            f"Duplicate note detected - Front: '{front.get_field_value()[:50]}...' "
                            f"from file '{note.source_file.file_name}' was not added. "
                            f"Note may already exist in Anki or Note ID in Obsidian may be incorrect."
                        )
            
            if add_response_no_duplicates:
                add_response = add_response_no_duplicates
                logger.info(f"Successfully added {len(add_response)} notes to Anki")
                if duplicates_count > 0:
                    logger.warning(f"Skipped {duplicates_count} duplicate notes")
            else:
                logger.warning("No notes were added - all were duplicates")
                
            return add_response
        except Exception as e:
            logger.error(f"Failed to add notes to Anki: {e}")
            raise

    def updates_existing_notes(self, notes: List[Note]) -> None:
        logger.info(f"Updating {len(notes)} existing notes...")
        if not notes:
            return
        multi_request = _create_multi_request(notes, AnkiUpdateNoteRequest)
        response = self._invoke_request(multi_request)

    def ensure_correct_deck(self, notes: List[Note]) -> None:
        logger.info("Ensuring correct deck for notes in anki")
        if not notes:
            return
        multi_request = _create_multi_request(notes, AnkiChangeDeckRequest)
        self._invoke_request(multi_request)

    def delete_notes(self, notes: List[Note]) -> None:
        logger.info("deleting notes in anki")
        if not notes:
            return
        self._invoke_request(AnkiDeleteNotesRequest(notes))

    def create_decks(self, decks: List[str]) -> None:
        if not decks:
            return
        logger.info(f"Making sure that these Decks exist: {list(decks)}")
        requests = [AnkiCreateDeckRequest(deck) for deck in decks]
        multi_request = AnkiMultiRequest(requests)
        self._invoke_request(multi_request)
