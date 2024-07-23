import re

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

from notes.transformers.utils import create_link
from utils.patterns import (
    IMAGE_FILE_WIKILINK_REGEX,
    AUDIO_FILE_REGEX,
    OBSIDIAN_LINKS_REGEX,
    OBS_INLINE_MATH_REGEX,
    OBS_DISPLAY_MATH_REGEX,
    IMAGE_URL_REGEX,
)


def replace_with_link(text: str, vault_name: str) -> str:
    def re_sub_repl_dynamic(match: re.Match) -> str:
        """
        this function satisfies the requirement of the interface for re.sub,
        which is to pass a function that takes a match object and returns a string
        """
        string = match.group(1)
        splitted_string = string.split("|")
        if len(splitted_string) > 1:  # if there is an alias
            file_name = splitted_string[0]
            alias = "".join(splitted_string[1:])
            return create_link(
                vault_name=vault_name, file_name=file_name, name_alias=alias
            )

        return create_link(vault_name=vault_name, file_name=match.group(1))

    return re.sub(OBSIDIAN_LINKS_REGEX, re_sub_repl_dynamic, text)


def to_anki_math_transformer(text: str) -> str:
    """
    we have 2 types of math formulas, inline and display
    inline math is wrapped in $ and display math is wrapped in $$
    we need to change the wrapping to anki wrapping which becomes [$$]...[/$$] and [$]...[/$]
    """
    text = re.sub(OBS_INLINE_MATH_REGEX, r"\\\(\1\\\\)", text)
    text = re.sub(OBS_DISPLAY_MATH_REGEX, r"\\\[\1\\\]", text)
    return text


def create_code_blocks_transformer(text: str) -> str:
    # fenced code so we can get the language and hilite to get the highlights with css
    text = markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            CodeHiliteExtension(css_class="highlight"),
            "footnotes",
            "md_in_html",
            "tables",
            "nl2br",
            "sane_lists",
        ],
    )
    return text


def format_pictures_to_html_transformer(text: str) -> str:
    """
    gets the 2nd and 3rd group which are the filename and extension
    replaces the whole match with the img tag html
    """
    text = re.sub(
        IMAGE_URL_REGEX, r'<img src="\1">', text
    )  # matches https links of images and replaces them with the img tag
    return re.sub(IMAGE_FILE_WIKILINK_REGEX, r'<img src="\2.\3">', text)


def format_audio_to_html_transformer(text: str) -> str:
    """
    gets the 2nd and 3rd group which are the filename and extension
    replaces the whole match with the img tag html
    """
    return re.sub(
        AUDIO_FILE_REGEX,
        r'<audio controls><source src="\2.\3" type="audio/\3"></audio>',
        text,
    )
