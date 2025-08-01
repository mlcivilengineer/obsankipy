# Obsankipy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Obsankipy is a Python tool that synchronizes Markdown notes from an Obsidian vault into Anki flashcards using the AnkiConnect API. It was inspired by the [Obsidian_to_Anki](https://github.com/ObsidianToAnki/Obsidian_to_Anki) plugin but is implemented entirely in Python, allowing it to run independently without the Obsidian application, thus enabling better automation.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Supported Note Types](#supported-note-types)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Multiple Card Types**: Supports basic, reversed, type-in-the-answer, and cloze cards
- **Rich Media Support**: Handles images, audio files, mathematical formulas, and code blocks
- **Smart Synchronization**: Automatically moves notes when the target deck changes
- **Flexible Filtering**: Excludes files or directories from scanning via configuration
- **Remote Support**: Works with local or remote AnkiConnect instances
- **Debug Logging**: Optional debug logging to `.obsankipy.log` file

### Advanced Features
- **Automatic Deck Management**: Notes are always placed in the correct target deck
- **Pattern-based Exclusion**: Use Unix patterns to exclude specific files from scanning
- **Directory Filtering**: Exclude dotted directories and custom directory patterns
- **Remote Anki Integration**: Connect to remote Anki instances for automation
- **Hash-based Change Detection**: Only processes modified files for efficiency

## Requirements

### Essential
- **Anki**: Running in the background
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**: Modern Python package manager
- **[AnkiConnect](https://foosoft.net/projects/anki-connect/)**: Anki plugin for API access
- **Python**: 3.12 or higher (Installed automatically by uv)

### Optional
- **CSS for syntax highlighting**: If you want your codeblocks to have syntax highlighting. See `examples/styles.css`.
- **Remote Anki setup**: For automation scenarios (see [anki-desktop-docker](https://github.com/mlcivilengineer/anki-desktop-docker))

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mlcivilengineer/obsankipy.git
cd obsankipy
```

### 2. Install uv Package Manager

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install AnkiConnect
1. Open Anki
2. Go to Tools → Add-ons
3. Click "Get Add-ons..." and enter code: `2055492159`
4. Restart Anki

## Quick Start

### Try the Example
With Anki open in the background, run the following in a Linux / MacOS Terminal or Windows Powershell:

```bash
uv run src/obsankipy.py examples/vault/.obsankipy/config.yaml
```

### Debug Mode
```bash
uv run src/obsankipy.py path/to/config.yaml --debug
```

All required Python packages are installed automatically on first run.

## Configuration

### Configuration File Structure

Create a `.obsankipy` directory inside your vault with a `config.yaml` file. The configuration has three main sections:

#### Minimal Configuration
```yaml
vault:
  dir_path: ./path/to/your/vault
  medias_dir_path: ./path/to/your/vault/Medias
regex:
  basic:
    - (?<=#spaced)\s*\n([\s\S]*?)\n([\s\S]*?(?=---|<!--|$(?![\r\n])))
globals:
  anki:
    url: http://localhost:8765
```

#### Complete Configuration Example
```yaml
# Optional: Custom cache directory for file hashes
hashes_cache_dir: ./examples/vault/.obsankipy

vault:
  dir_path: ./examples/vault
  medias_dir_path: ./examples/vault/Medias
  exclude_dotted_dirs_from_scan: true  # Excludes directories starting with '.'
  exclude_dirs_from_scan:              # Custom directories to exclude
    - Templater
    - Templates
  file_patterns_to_exclude:            # Unix patterns for file exclusion
    - ".*"                            # Excludes files starting with '.'
    - "*.tmp"                         # Excludes temporary files

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
    deck_name: Default                 # Default deck for new cards
    tags:                             # Default tags for all cards
      - Obsidian
      - Flashcards
    url: http://localhost:8765        # AnkiConnect URL
    fine_grained_image_import: false  # Advanced image handling
```

### Configuration Options Explained

#### Vault Section
- `dir_path`: Path to your Obsidian vault
- `medias_dir_path`: Path to media files (images, audio)
- `exclude_dotted_dirs_from_scan`: Skip directories starting with '.'
- `exclude_dirs_from_scan`: List of specific directories to skip
- `file_patterns_to_exclude`: Unix patterns for file exclusion

#### Regex Section
Define patterns for different note types. Each pattern must capture:
1. **Group 1**: Question/Front of card
2. **Group 2**: Answer/Back of card

#### Globals Section
- `deck_name`: Default Anki deck
- `tags`: Default tags applied to all cards
- `url`: AnkiConnect endpoint
- `fine_grained_image_import`: Advanced image processing

## Supported Note Types

All the basic anki note types are supported. You can customize how all the note types will be captured. The default way that they will be captured is the following:

### Basic Cards
```markdown
#spaced
What is the capital of France?

Paris is the capital of France.
+++
```

### Basic Reversed Cards
```markdown
#reversed
Python

A high-level programming language
+++
```

### Type-in-the-Answer Cards
```markdown
#type
What does CPU stand for?

Central Processing Unit
+++
```

### Cloze Cards
```markdown
The {{c1::mitochondria}} is the {{c2::powerhouse}} of the cell.
```

### Alternative Q&A Format
```markdown
Q: What is machine learning?

A: A subset of artificial intelligence that enables computers to learn without being explicitly programmed.
+++
```

## Advanced Usage

### Custom Regex Patterns

You can define custom regex patterns for note extraction. Requirements:
- **Group 1**: Question content
- **Group 2**: Answer content
- **Positive lookahead**: Define note termination patterns

Example pattern breakdown:
```regex
([\s\S]*?(?=\+\+\+|---|<!--|$(?![\r\n])))
```

- `([\s\S]*?)`: Non-greedy capture of any character
- `(?=\+\+\+|---|<!--|$(?![\r\n]))`: Lookahead for terminators:
  - `\+\+\+`: Three plus symbols
  - `---`: Three hyphens  
  - `<!--`: HTML comment start
  - `$(?![\r\n])`: End of file

### Frontmatter Support

Control card properties using YAML frontmatter:

```markdown
---
target deck: Spanish Vocabulary
tags: spanish, verbs, beginner
---

#spaced
How do you say "to speak" in Spanish?

hablar
+++
```

### Media Support

#### Images
```markdown
# Markdown format
![Description](image.png)

# Wikilink format  
![[image.png]]

# External URLs
![Alt text](https://example.com/image.png)
```

#### Audio
```markdown
![[audio_file.mp3]]
```

#### Math Formulas
```markdown
# Display math
$$E = mc^2$$

# Inline math
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
```

#### Code Blocks
```markdown
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Remote Anki Setup

For automation or remote deployments:

1. **Configure remote URL**:
   ```yaml
   globals:
     anki:
       url: http://remote-server:8765
   ```

2. **Docker deployment**: Consider using [anki-desktop-docker](https://github.com/mlcivilengineer/anki-desktop-docker)

3. **Security**: Ensure AnkiConnect is properly secured for remote access

## Examples

### Example Note File
See `examples/vault/test file.md` for a comprehensive example showing:
- Multiple card types
- Media embedding
- Math formulas
- Code blocks
- Wikilinks


### Performance Tips

1. **Use file exclusion patterns** to skip unnecessary files
2. **Enable hash caching** for large vaults
3. **Exclude template directories** from scanning
4. **Use specific regex patterns** to avoid false matches

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the `obsidian_to_anki` plugin
- Built with modern Python tooling using `uv`
- Leverages the powerful AnkiConnect API

---

**Need help?** Check the [examples](examples/) directory or open an issue on GitHub.
