#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#    "annotated-types==0.6.0",
#    "certifi==2023.11.17",
#    "charset-normalizer==3.3.2",
#    "idna==3.6",
#    "markdown==3.5.1",
#    "pydantic==2.5.2",
#    "pydantic-core==2.14.5",
#    "pygments==2.17.2",
#    "python-frontmatter==1.0.1",
#    "pyyaml==6.0.1",
#    "requests==2.31.0",
#    "typing-extensions==4.8.0",
#    "urllib3==2.1.0",
# ]
# ///
"""Script for adding cards to Anki from Obsidian."""

import logging
from pathlib import Path

import yaml

from config_parser import NewConfig
from run import run
from utils.helpers import setup_cli_parser, setup_root_logger


def main():
    """Main functionality of script."""

    args = setup_cli_parser()
    setup_root_logger(args.debug)
    logger = logging.getLogger(__name__)
    logger.info("Starting script")
    try:
        with open(Path(args.config_path), "r") as f:
            config = yaml.safe_load(f)
        new_config = NewConfig(**config)
    except Exception as err:
        logger.exception(f"Error parsing config file")
        raise

    run(new_config)


if __name__ == "__main__":
    main()
