import argparse
import base64
import fnmatch
import hashlib
import json
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import List

from utils.constants import SUPPORTED_TEXT_EXTS
from utils.patterns import ID_DELETE_REGEX

logger = logging.getLogger(__name__)


def overwrite_file_safely(file_path, contents):
    """Safely overwrite a file using a temporary file to prevent data loss."""
    logger.debug(f"Safely overwriting file: {file_path}")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_path = temp_file.name
        # Write contents to the temporary file
        temp_file.write(contents)

    try:
        # Replace the original file with the temporary file
        shutil.move(temp_path, file_path)
        logger.debug(f"File '{file_path}' successfully overwritten safely")

    except Exception as err:
        # If an error occurs, remove the temporary file
        logger.error(f"Failed to overwrite file '{file_path}': {err}")
        os.remove(temp_path)
        raise Exception(
            f"Error writing to file. Temporary file removed. Original error: {err}"
        ) from err


def string_insert(string, position_inserts):
    """
    Insert strings in position_inserts into string, at indices.

    position_inserts will look like:
    [(0, "hi"), (3, "hello"), (5, "beep")]
    """
    offset = 0
    position_inserts = sorted(list(position_inserts))
    for position, insert_str in position_inserts:
        string = "".join(
            [string[: position + offset], insert_str, string[position + offset :]]
        )
        offset += len(insert_str)
    return string


def get_files_paths(
    dir_path, exclude_dirs=None, exclude_dotted_dirs=True, patterns_to_exclude=None
) -> List[Path]:
    """Get all files in this directory recursively."""
    all_files = []
    if exclude_dirs is None:
        exclude_dirs = []
    if patterns_to_exclude is None:
        patterns_to_exclude = []
    for root, dirs, files in os.walk(dir_path):
        files = [
            filename
            for filename in files
            if not any(
                fnmatch.fnmatch(filename, pattern) for pattern in patterns_to_exclude
            )
        ]
        if exclude_dirs:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        if exclude_dotted_dirs:
            dirs[:] = [
                d for d in dirs if not d.startswith(".")
            ]  # exclude hidden dirs, very cryptic way of doing it
        for file in files:
            for extension in SUPPORTED_TEXT_EXTS:
                if file.endswith(extension):
                    all_files.append(Path(root) / file)
    return all_files


def erase_note_ids_in_the_files(file_paths: List[Path]):
    """Erase the note IDs from the files."""
    if not file_paths:
        logger.info("No files to erase note IDs from")
        return
        
    logger.info(f"Erasing note IDs from {len(file_paths)} files...")
    for file_path in file_paths:
        erase_note_id_in_the_file(file_path)
    logger.info("Successfully erased note IDs from all files")


def erase_note_id_in_the_file(file_path: Path):
    """Erase note IDs from a single file."""
    logger.debug(f"Erasing note IDs from file: {file_path}")
    try:
        with open(file_path, "r") as f:
            file_content = f.read()
        
        original_length = len(file_content)
        file_content = re.sub(ID_DELETE_REGEX, "", file_content)
        new_length = len(file_content)
        
        if original_length != new_length:
            logger.debug(f"Removed {original_length - new_length} characters (note IDs) from {file_path}")
        
        overwrite_file_safely(file_path, file_content)
    except Exception as e:
        logger.error(f"Failed to erase note IDs from {file_path}: {e}")
        raise


def file_encode(filepath):
    """Encode the file as base 64."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def compute_hash(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()


def clear_file_hashes(hashes_cache_dir):
    try:
        logger.info("Clearing file hashes")
        with open(hashes_cache_dir, "w") as f:
            f.write("[]")
    except FileNotFoundError:
        return


def open_cache(hashes_path: Path):
    """Open and load the file hash cache."""
    try:
        logger.debug(f"Opening cache file at {hashes_path}")
        with open(hashes_path, "r") as f:
            cache = json.loads(f.read())
        logger.debug(f"Loaded {len(cache)} file hashes from cache")
        return cache
    except FileNotFoundError:
        logger.info(f"Cache file not found at {hashes_path}, starting with empty cache")
        return []
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in cache file {hashes_path}: {e}. Starting with empty cache")
        return []


def setup_cli_parser():
    """Set up the command-line argument parser."""
    parser = argparse.ArgumentParser()
    # Positional argument
    parser.add_argument(
        "config_path",
        metavar="config_path",
        type=str,
        help="Path to the configuration file",
    )
    # Optional arguments
    parser.add_argument(
        "--config_path",
        "-c",
        type=str,
        help="Path to the configuration file (alternative to the positional argument)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="activates the debug log file",
    )
    args = parser.parse_args()
    return args


def write_hashes_to_file(curr_hashes, hashes_path: Path):
    """Write current file hashes to cache file."""
    logger.debug(f"Writing {len(curr_hashes)} file hashes to cache at {hashes_path}")
    try:
        with open(hashes_path, "w") as f:
            f.write(json.dumps(curr_hashes))
        logger.debug("Successfully updated hash cache file")
    except Exception as e:
        logger.error(f"Failed to write hash cache to {hashes_path}: {e}")
        raise


def setup_root_logger(debug=False):
    root_logger = logging.getLogger("")
    root_logger.setLevel(logging.DEBUG)
    if debug:
        file_handler = logging.FileHandler(".obsankipy.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s:::%(levelname)s:::%(funcName)s:::%(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s:::%(levelname)s:::%(message)s")
    console_handler.setFormatter(console_formatter)

    # Get the root logger

    # Add the handlers to the root logger
    root_logger.addHandler(console_handler)
