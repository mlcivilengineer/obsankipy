import re
from .constants import SUPPORTED_AUDIO_EXTS, SUPPORTED_IMAGE_EXTS

SUPPORTED_IMAGE_EXTS = "|".join(SUPPORTED_IMAGE_EXTS)
SUPPORTED_AUDIO_EXTS = "|".join(SUPPORTED_AUDIO_EXTS)

IMAGE_FILE_WIKILINK_PATTERN = rf"!\[\[(?P<path>[.|/\\]?.*[/|\\])?(?P<filename>/?.*?)\.(?P<extension>({SUPPORTED_IMAGE_EXTS}))]]"
IMAGE_FILE_WIKILINK_REGEX = re.compile(
    IMAGE_FILE_WIKILINK_PATTERN,
    re.IGNORECASE,
)

IMAGE_FILE_MARKDOWN_PATTERN = rf"!\[.*\]\((?!http[s]?)(?P<path>[.|/\\]?.*[/|\\])?(?P<filename>/?.*?)\.(?P<extension>({SUPPORTED_IMAGE_EXTS}))\)"
IMAGE_FILE_MARKDOWN_REGEX = re.compile(
    IMAGE_FILE_MARKDOWN_PATTERN,
    re.IGNORECASE,
)

IMAGE_URL_PATTERN = rf"\s(http[s]?:\/\/\S+\.(?:{SUPPORTED_IMAGE_EXTS}))\s"
IMAGE_URL_REGEX = re.compile(IMAGE_URL_PATTERN, re.IGNORECASE)

AUDIO_FILE_PATTERN = rf"!\[\[(?P<path>[.|/\\]?.*[/|\\])?(?P<filename>/?.*?)\.(?P<extension>({SUPPORTED_AUDIO_EXTS}))]]"
AUDIO_FILE_REGEX = re.compile(
    AUDIO_FILE_PATTERN,
    re.IGNORECASE,
)

OBSIDIAN_LINKS_REGEX = r"(?<!!)\[\[([^\n]*?)\]\]"  # this should handle getting the file names for links, excluding aliases
OBSIDIAN_LINKS_REGEX = re.compile(OBSIDIAN_LINKS_REGEX)

OBS_INLINE_MATH_PATTERN = "(?<!\$)\$((?=[\S])(?=[^$])[\s\S]*?\S)\$"
OBS_INLINE_MATH_REGEX = re.compile(OBS_INLINE_MATH_PATTERN)

OBS_DISPLAY_MATH_PATTERN = "\$\$([\s\S]*?)\$\$"
OBS_DISPLAY_MATH_REGEX = re.compile(OBS_DISPLAY_MATH_PATTERN)

ID_REGEX_PATTERN = r"(?P<id_str><!--ID: (?P<id_num>\d+)-->)?(?P<delete>#DELETE)?"  # this regex will be appended to the main regex to check for the id and delete tag, they will be optional

ID_DELETE_REGEX_PATTERN = r"(?P<id_str><!--ID: (?P<id_num>\d+)-->(?P<delete>#DELETE))\b"  # this regex will match the id and the delete tag, they are required in order to match
ID_DELETE_REGEX = re.compile(ID_DELETE_REGEX_PATTERN)
