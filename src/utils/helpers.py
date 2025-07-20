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
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_path = temp_file.name
        # Write contents to the temporary file
        temp_file.write(contents)

    try:
        # Replace the original file with the temporary file
        shutil.move(temp_path, file_path)
        logger.info(f"File '{file_path}' successfully overwritten.")

    except Exception as err:
        # If an error occurs, remove the temporary file
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
    for file_path in file_paths:
        erase_note_id_in_the_file(file_path)


def erase_note_id_in_the_file(file_path: Path):
    with open(file_path, "r") as f:
        file_content = f.read()
    file_content = re.sub(ID_DELETE_REGEX, "", file_content)
    overwrite_file_safely(file_path, file_content)


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
    try:
        logger.info(f"Opening cache file at {hashes_path}")
        with open(hashes_path, "r") as f:
            cache = json.loads(f.read())
        return cache
    except FileNotFoundError:
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
    with open(hashes_path, "w") as f:
        f.write(json.dumps(curr_hashes))

def setup_root_logger(debug=False):
    root_logger = logging.getLogger("")
    root_logger.setLevel(logging.DEBUG)  # Capture all logs, handlers will filter

    # Remove existing handlers to prevent duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Formatter: structured, add timestamp only in debug
    if debug:
        formatter = logging.Formatter(
            "%(asctime)s ::: %(levelname)s ::: %(name)s ::: %(funcName)s ::: %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(message)s"
        )

    # Console handler: INFO or higher
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if not debug else logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if debug:
        # File handler for debug logs
        file_handler = logging.FileHandler(".obsankipy.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
