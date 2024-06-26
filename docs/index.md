# TexnoMagic

**TexnoMagic** is a free and open source Python 3 library, CLI and format for
**symbol recognition** and symbol-based language parsing.

I created **TexnoMagic** after prototyping serveral systems for magic
symbol recognition and invocation as well as systems for creating magic
language based on symbols.

You can read my posts about

* [Theory of Magic](https://texnoforge.dev/words-of-power-devlog-1-theory-of-magic.html)
* [Invocation of Magic](https://texnoforge.dev/words-of-power-devlog-2-invocation-of-magic.html)
* [Introducing TexnoMagic](https://texnoforge.dev/n/words-of-power-devlog-6-introducing-texnomagic/)
* [Words of Power](https://texnoforge.dev/words-of-power/)

to get a better idea of what I'm trying to achieve.

See [TexnoLatin](https://github.com/texnoforge/texnolatin) reference alphabet.


## Status: alpha

**alpha**: working well, but interfaces aren't final yet

JSON-RPC is currently broken on Python **3.12** due to `jsonrpcserver` / `oslash` dep
[breakage](https://github.com/explodinglabs/jsonrpcserver/issues/273).
`jsonrpcserver` is now an optional dep not installed by default to enable
running of Python 3.12 before this gets fixed.

**[TexnoMagic News](news.md)**


### Features

- portable open format based on proven and widely supported standards:
  - JSON for metadata
  - CSV for symbol drawing data (fast and easy to parse)
  - SVG for infinitely scalable symbol images
- provide consistent and practical directory structure
- save and load symbols to/from well-defined user files
- manage symbols in alphabets
- manage training data (drawings) for individual symbols
- download and use mods from [wop.mod.io] mod portal easily
- train symbol models from drawings
  - currently uses Gaussian Mixture Models (GMM)
  - neural networks support is possible
- use symbol models for real-time symbol recognition
- spell language parser based of Parsing Expression Grammars (PEG)
- tests, linting, CI
- proper python packaging, available from [PyPI]
- interfaces:
  - Python module (`texnomagic`)
  - Command-Line Interface (`texnomagic.cli`)
  - simple TCP server using JSON-RPC (`texnomagic.server`) - universal interface
- ⚠ format and API aren't final yet
- ⚠ docs need more content


## Install

TexnoMagic is available from [PyPI] for Python **3.10+** (latest tested: **3.12**):

```
pip install texnomagic
```

You can install / develop / build from source as with any other python module.


```
cd texnomagic

# install from source
pip install .

# install in --editable mode (great for development)
pip install -e .

# isolated install using pipx
pipx install .

# build package
python -m build
```


## Use


### CLI ⌨️

A full-featured `git`-like Command-Line Interface with colors support is
available through `texnomagic` script.

The `texnomagic` script should be installed by default, run it without arguments
to get a summary of avaliable commands options:

```
$> texnomagic

Usage: texnomagic [OPTIONS] COMMAND [ARGS]...

  TexnoMagic CLI

Options:
  --version   Show TexnoMagic version and exit.
  -h, --help  Show this message and exit.

Commands:
  abc      Manage TexnoMagic alphabets.
  drawing  Manage TexnoMagic drawings.
  mod      Manage Words of Power mods.
  server   Start TexnoMagic TCP server on PORT.
  spell    Parse and work with TexnoMagic Spells.
  symbol   Manage TexnoMagic symbols.
```

Add `-h`/`--help` after a command to get usage for that command:

```
$> texnomagic symbol -h

Usage: texnomagic symbol [OPTIONS] COMMAND [ARGS]...

  Manage TexnoMagic symbols.

Options:
  -h, --help  Show command help.

Commands:
  list  List all symbols in a TexnoMagic alphabet.
  new   Create a new TexnoMagic symbol.
  show  Show details of a TexnoMagic symbol.
```

If your shell doesn't see the script (i.e. when not in `$PATH`), you can invoke
the `texnomagic.cli` module directly:

```
$> python -m texnomagic.cli list-abcs --full
```

### Python 🐍

You can find code examples in:

* [texnomagic/commands](https://github.com/texnoforge/texnomagic/tree/master/texnomagic/commands)
* [texnomagic/requests.py](https://github.com/texnoforge/texnomagic/blob/master/texnomagic/requests.py)
* [tests/](https://github.com/texnoforge/texnomagic/tree/master/tests)


### GUI 🖱️

[wopeditor] is a project dedicated to providing comprehensive GUI for
TexnoMagic.


### Godot Engine ⚙️

[wopeditor] contains GDScript implementation of client for TexnoMagic
server: [wopeditor.client].

You can use Godot's `JSONRPC` module to form requests and send them as strings
using standard Godot networking which TexnoMagic adpoted (messages prefixed with
4 bytes of total message length).


### JSON-RPC 🌍

You can start universal language-agnostic JSON-RPC over TCP server using `texnomagic` CLI:

```
texnomagic server

# optionally select a port
texnomagic server 12345
```

You can also invoke [texnomagic.server] module directly:

```
python -m texnomagic.server
```

It's also possible to compile stand-alone `texnomagic` binary using PyInstaller:

```
pyinstaller texnomagic.spec
# results in dist/texnomagic
```

Simple reference python client is provided in [texnomagic.client] although it's
only used for testing in TexnoMagic.

For a full-fledged client implementation see [wopeditor.client].


## Bugs and Feature Requests

Please use [GitHub Issues](https://github.com/texnoforge/texnomagic/issues)
to report any problems or feature requests.

Contributions, suggestions, and ideas are always welcome ♥


## Contact

Feel free to drop by
[#wopeditor @ texnoforge discord](https://discord.gg/Dq3vaeg3pG).


[wopeditor]: https://texnoforge.github.io/wopeditor/
[texnomagic.client]: https://github.com/texnoforge/texnomagic/blob/master/texnomagic/client.py
[texnomagic.server]: https://github.com/texnoforge/texnomagic/blob/master/texnomagic/server.py
[wopeditor.client]: https://github.com/texnoforge/wopeditor/blob/master/texnomagic/client.gd
[PyPI]: https://pypi.org/project/texnomagic/
[wop.mod.io]: https://wop.mod.io
