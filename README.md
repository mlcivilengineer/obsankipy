# Obsankipy

Obsankipy synchronizes Markdown notes from an Obsidian vault into Anki by using the AnkiConnect API. It was inspired by the `obsidian_to_anki` plugin but is implemented entirely in Python so it can run without the Obsidian application.

## Features

- Supports basic, reversed and cloze cards
- Handles images, audio, math and code blocks
- Automatically moves notes when the target deck changes
- Excludes files or directories from scanning via configuration
- Works with a local or remote AnkiConnect instance
- Optional debug logging to a `.obsankipy.log` file

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [AnkiConnect](https://foosoft.net/projects/anki-connect/)

Optional tools:

- CSS for syntax highlighting (see `examples/styles.css`)

## Installation

1. Clone this repository.
2. Install `uv`:

Linux / Mac:
   ```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

Windows:
   ```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. Run the script with your configuration file:
   ```bash
   uv run src/obsankipy.py path/to/config.yaml
   ```
   All required Python packages will be installed automatically on first run.

## Quick start

A sample vault with a configuration file is provided in `examples/vault`. To try it out:

```bash
uv run src/obsankipy.py examples/vault/.obsankipy/config.yaml
```

## Configuration

Create a `.obsankipy` directory inside your vault with a `config.yaml` file. The configuration has three main sections:

- **vault** – path to the vault and media directory
- **regex** – patterns used to find notes in Markdown files
- **globals** – default Anki deck, tags and AnkiConnect URL

A minimal configuration looks like:

```yaml
vault:
  dir_path: ./examples/vault
  medias_dir_path: ./examples/vault/Medias
regex:
  basic:
    - (?<=#spaced)\s*\n([\s\S]*?)\n([\s\S]*?(?=---|<!--|$(?![\r\n])))
globals:
  anki:
    url: http://localhost:8765
```

See `examples/vault/.obsankipy/config.yaml` for a full example with additional options.

## Supported default note types

### Basic
```markdown
#spaced
Question

Answer
+++
```

### Basic reversed
```markdown
#reversed
Question

Answer
+++
```

### Type in the answer
```markdown
#type
Question

Answer
+++
```

### Cloze
```markdown
this is a {{c1::cloze}} card
```
### Custom Regex Instructions
If you want to use your own regex you just have to implement it in such a way that
the first group is the question and the second group is the answer. It also has to have a
positive lookahead that dictates what is the termination of the note, including
the <!--ID: as a termination possibility, as that will be the note id, for example:
```bash
(?=---|<!--ID: )
```
will assert that the end of the note has to find --- or <!--ID: in the note.

Also the program will append the following to the end of the regex
in order to find the id numbers if they exist:
```bash
(?P<id_str><!--ID: (?P<id_num>\d+)-->)?(?P<delete>#DELETE)?
```
so make sure that your regex works with this appended to the end of it.

A good example of Answer capturing group is:
```regexp
([\s\S]*?(?=\+\+\+|---|<!--|$(?![\r\n])))
```
It matches a block of text until it finds one of the delimiters or the end of the file.
Breaking it down:

```text
([\s\S]*?): This is a non-greedy capturing group that matches any character 
(including whitespace and non-whitespace) zero or more times until the next 
part of the pattern is satisfied.

(?=\+\+\+|---|<!--|$(?![\r\n])): This is a positive lookahead assertion ((?= ... )). 
It checks that the text ahead of the current position matches one of the following alternatives:

\+\+\+: Matches three plus symbols.
---: Matches three hyphens.
<!--: Matches an HTML comment start.
$(?![\r\n]): This part is checking for the end of the file.
```

Some useful things that you can't do with obsidian_to_anki but is supported by obsankipy:
- anki note is always at the correct target deck, so if you change the target deck in the obsidian note frontmatter, the program will move it to the correct deck.
- prevent running the scan on specific files that follow some pattern, for example, if you have a file that you don't want to be scanned, you can just add a [unix pattern](https://docs.python.org/3/library/fnmatch.html) to the config file and the program will ignore it.
- prevent running the scan against directories that start with a dot
- prevent running the scan against directories that you specify in the config file
- run the scan and add notes to a remote anki instance, so you don't need to have anki running locally in the same computer. Just specify the URL of the remote anki instance in the config file. (good for automation on rasperry pi or other computers, make sure to look at my other project [anki-desktop-docker](https://github.com/mlcivilengineer/anki-desktop-docker) which lets you run anki on a docker container)

The program can also run in --debug mode by passing this argument through the cli like this:
```bash
python ./src/obsankipy.py ./examples/vault/.obsankipy/config.yaml --debug
```
This will setup a logfile called .obsankipy.log in the current working directory, so you can check it for errors.
