from urllib.parse import quote


def create_url(vault_name: str, file_name: str) -> str:
    return f"obsidian://open?vault={quote(vault_name)}&file={quote(file_name)}"


def create_link(vault_name: str, file_name: str, name_alias=None) -> str:
    if not name_alias:
        name_alias = file_name
    return f'<a href="{create_url(vault_name=vault_name, file_name=file_name)}">{name_alias}</a>'
