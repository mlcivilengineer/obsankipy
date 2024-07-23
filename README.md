# Obsankipy
Inspired by [obsidian_to_anki](https://github.com/Pseudonium/Obsidian_to_Anki) plugin, I decided to write my own program to sync my notes 
from obsidian to anki in the Python language, so that I could run it without having obsidian 
running, as well as do some automation with it.

It does not support all the features of obsidian_to_anki, but it does support the most important ones
like basic and reversed cards, cloze cards, images, audio, math formulas, code blocks, links, etc.

This is still a work in progress, so expect bugs and missing features. Hope you find it useful.

## Requirements
- Python 3.10 or higher (might work with older versions, but not tested)
- AnkiConnect

### optional requirements
- css applied in anki if you want syntax highlighting in code blocks. The css needed is in the examples folder.
- pipx (for development)
- poetry (for development)

## Installation

Clone the repository or download the zip file and extract it.

Run pip install against the requirements.txt file to install the program dependencies in your system:
```bash
pip install -r requirements.txt
```

Then you can open up a terminal in the program folder and run the program against the example vault to see it in action by calling the main script 
and passing the path to the config file:
```bash
python ./src/obsankipy.py ./examples/vault/.obsankipy/config.yaml
```



## Usage
You should use the config.yaml file as a template for your own config.
Create a `.obsankipy` folder in your vault and put the config file there.
The config file is divided into 3 sections:
- `vault`: contains the path to the vault and some settings
- `regex`: contains the regexes used to parse the markdown files for each note type
- `globals`: contains the global settings for the program, like the default deck, the default tags, etc.

minimum config.yaml file:
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

a more complete config.yaml file with all the options:
```yaml
#hashes_cache_dir: ./examples/vault/.obsankipy
vault:
  dir_path: ./examples/vault
  medias_dir_path: ./examples/vault/Medias
  exclude_dotted_dirs_from_scan: true # excludes directories that start with a dot
  exclude_dirs_from_scan:
    - Templater
  file_patterns_to_exclude:
    - ".*" # excludes files that start with a dot
regex:
  basic:
    - '(?<=#spaced)\s*\n([\s\S]*?)\n([\s\S]*?(?=\+\+\+|---|<!--|$(?![\r\n])))'
    - '^Q: ((?:.+\n)*)\n*A: ([\s\S]*?(?=\+\+\+|---|<!--ID: ))'
  basic_reversed:
    - '(?<=#reversed)\s*\n([\s\S]*?)\n([\s\S]*?(?=\+\+\+|---|<!--|$(?![\r\n])))'
  type_answer:
    - '(?<=#type)\s*\n([\s\S]*?)\n([\s\S]*?(?=\+\+\+|---|<!--|$(?![\r\n])))'
  cloze:
    - '((?!.*{{c\d+::[^}]*}[^}]).*{{c\d+::[^}]*}}.*\n)'

globals:
  anki:
    deck_name: Default
    tags:
      - Obsidian
    url: http://localhost:8765
```


The supported note types are:
### Basic
The default regex expects the following format:
```markdown
#spaced
This is a question

This is an answer

The answer can be in multiple paragraphs
+++

or

Q: This is a question
A: This is an answer

which can also be in multiple paragraphs
+++

```
### Basic (and reversed card)
The default regex expects the following format:
```markdown
#reversed
This is a question

This is an answer
+++
```

### Type in the answer
The default regex expects the following format:
```markdown
#type
This is a question

This is an answer
+++
```

### Cloze
The default regex expects the following format:
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

The program supports deleting notes from anki, by appending a #DELETE to the end of the note id, for ex:

```markdown
#spaced
This is a question
This is the answer
<!--ID: 123-->#DELETE
+++
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
