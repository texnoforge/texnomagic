# TexnoMagic News

## texnomagic 0.7.1

!!! WARNING
    Not Yet Released - In Development

Released 2024-04-??

### Improvements

- `jsonrpcserver` dep is now optional, enabling Python >= 3.12
    - Add Python 3.12 job to CI
- new `texnomagic drawing recognize` command to recognize a [Drawing](drawing.md)
    - a powerful command with many useful options, see `--help`
- new `texnomagic drawing render` command to render [Drawing](drawing.md) to image such as PNG
    - only available when `pillow` module is installed
- new commands to normalize [Drawings](drawing.md):
    - `texnomagic drawing normalize`
    - `texnomagic symbol normalize`
    - `texnomagic abc normalize`
- new `texnomagic paths` command to show/create/open alphabets paths
- new `-C`/`--color` global option to control output color
- new [Drawing](drawing.md), [Symbol](symbol.md), and [Alphabet](abc.md) reference docs using `mkdocstrings`
    - add docstrings and type hints - nicer code AND docs
    - bump minimal Python to 3.10 due to typing improvements
- new [Cookbook](cookbook.md) doc with CLI and Python examples
    - executed using `markdown-exec` - always up-to-date
    - CLI examples including ANSI color
- better Symbol recognition tests
- various code and flow improvements

## texnomagic 0.7.0

Released 2024-02-29

### Improvements

- new ergonomic Command-Line Interface (CLI)
    - structured modular commands as seen in `git`
    - dedicated command modules in `texnomagic.commands` for better modularity
- terminal colors support using [rich](https://github.com/Textualize/rich) (new dep)
- basic symbol images support (`symbol.get_image_path()` and friends)
- improved symbol and alphabet representations and pretty printing
- improved python packaging using [hatch](https://hatch.pypa.io/) through `pyproject.toml`
    - update PyInstaller spec
- improved CI
    - add Python 3.11 job
    - separate lint job
- improved and updated docs
    - add this news page
    - mention current [problems](https://github.com/explodinglabs/jsonrpcserver/issues/273)
      with Python 3.12
    - mention [TexnoLation](https://github.com/texnoforge/texnolatin) reference alphabet
    - use [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) theme
