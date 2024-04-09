# TexnoMagic News

## texnomagic 0.7.1

!!! WARNING
    Not Yet Released - In Development

Released 2024-04-??

### Improvement

- `jsonrpcserver` dep is now optional, enabling Python >= 3.12
    - Add Python 3.12 job to CI
- new useful commands:
    - `texnomagic drawing recognize`
    - `texnomagic drawing normalize`
    - `texnomagic symbol normalize`
    - `texnomagic abc normalize`
- more comments and doc strings in interesting places
- small code and flow improvements

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
