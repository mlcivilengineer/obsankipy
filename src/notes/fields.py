from functools import partial
from typing import Protocol, List, Any

from notes.transformers.fields import (
    replace_with_link,
    format_pictures_to_html_transformer,
    format_audio_to_html_transformer,
    to_anki_math_transformer,
    create_code_blocks_transformer,
)
from notes.transformers.utils import create_link


class NoteField(Protocol):
    field_name: str
    text: str
    transformers: List[Any]

    def transform(self):
        pass

    def get_field_name(self):
        pass

    def get_field_value(self):
        pass


class FrontField:
    text: str
    vault_name: str
    source_file_name: str

    def __init__(self, text, vault_name, source_file_name, field_name=None):
        if not field_name:
            self.field_name = "Front"
        else:
            self.field_name = field_name
        self.text = text
        url_link_to_file = create_link(
            vault_name=vault_name,
            file_name=source_file_name,
            name_alias="Obsidian",
        )
        append_url_transformer = (
            lambda text: text + "<br>" + url_link_to_file
        )  # puts a line break and the link to the file in the end of the field

        # freezes the vault_name parameter so we can satisfy the interface that
        # the transform_back and transform_front accepts, which are functions that have the signature
        # (str) -> (str), we could have created a closure but this is an alternative method
        links_creator_transformer = partial(replace_with_link, vault_name=vault_name)

        self.transformers = [
            format_pictures_to_html_transformer,
            format_audio_to_html_transformer,
            to_anki_math_transformer,
            create_code_blocks_transformer,
            append_url_transformer,
            links_creator_transformer,
        ]

    def transform(self):
        for transformer in self.transformers:
            self.text = transformer(self.text)
        return self

    def get_field_name(self):
        return self.field_name

    def get_field_value(self):
        return self.text


class BackField:
    text: str
    vault_name: str

    def __init__(self, text, vault_name, field_name=None):
        if not field_name:
            self.field_name = "Back"
        else:
            self.field_name = field_name
        self.text = text

        links_creator_transformer = partial(replace_with_link, vault_name=vault_name)

        self.transformers = [
            format_pictures_to_html_transformer,
            format_audio_to_html_transformer,
            to_anki_math_transformer,
            create_code_blocks_transformer,
            links_creator_transformer,
        ]

    def transform(self):
        for transformer in self.transformers:
            self.text = transformer(self.text)
        return self

    def get_field_name(self):
        return self.field_name

    def get_field_value(self):
        return self.text
