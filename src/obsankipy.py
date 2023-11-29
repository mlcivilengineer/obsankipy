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
        logger.error(f"Error parsing config file: {err}")
        raise Exception(f"Error parsing config file: {err}") from err

    run(new_config)


if __name__ == "__main__":
    main()
