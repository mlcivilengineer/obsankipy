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
#    "pydantic==2.11.7",
#    "pydantic-core==2.33.2",
#    "pygments==2.17.2",
#    "python-frontmatter==1.0.1",
#    "pyyaml==6.0.1",
#    "requests==2.31.0",
#    "typing-extensions==4.14.1",
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

    logger.info("")  # Blank line
    logger.info("=" * 60)
    logger.info("🔁 Starting Obsankipy — Obsidian ↔ Anki Synchronization".center(60))
    logger.info("=" * 60)
    logger.info("")  # Blank line
    logger.info(f"🛠️  Configuration file: {args.config_path}")
    logger.info(f"{'🔍' if args.debug else '📦'} Debug mode: {'enabled' if args.debug else 'disabled'}")

    try:
        logger.info("📄 Loading configuration file...")
        with open(Path(args.config_path), "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info("✅ Configuration loaded successfully")

        logger.info("🧪 Parsing and validating configuration...")
        new_config = NewConfig(**config)
        logger.info("✅ Configuration validation completed")

    except FileNotFoundError:
        logger.error("❌ Configuration file not found!")
        raise
    except yaml.YAMLError as e:
        logger.error("❌ Invalid YAML syntax in configuration file!")
        raise
    except Exception as e:
        logger.error("❗ Unexpected error while parsing configuration!")
        raise

    logger.info("🚀 Starting synchronization process...")
    try:
        run(new_config)
        logger.info("")  # Blank line
        logger.info("=" * 60)
        logger.info("✅ Obsankipy synchronization completed successfully!".center(60))
        logger.info("=" * 60)
    except Exception as e:
        logger.info("")  # Blank line
        logger.error("=" * 60)
        logger.error("💥 Obsankipy synchronization failed!".center(60))
        logger.error(f"❗ Error: {e}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    main()

