# TexnoMagic

**TexnoMagic** is a free and open source Python 3 library and format for magic
symbol recognition and symbol-based language parsing.

I created **TexnoMagic** after prototyping serveral systems for magic
symbol recognition and invocation as well as systems for creating magic
language based on symbols.

You can read my posts about

* [Theory of Magic](https://texnoforge.dev/words-of-power-devlog-1-theory-of-magic.html)
* [Invocation of Magic](https://texnoforge.dev/words-of-power-devlog-2-invocation-of-magic.html)
* [Introducing TexnoMagic](https://texnoforge.dev/n/words-of-power-devlog-6-introducing-texnomagic/)
* [Words of Power](https://texnoforge.dev/words-of-power/)

to get a better idea of what I'm trying to achieve.


## Status

**alpha**: integration with [wopeditor]/Godot and [wop.mod.io] mod portal

* save and load symbols to/from user files
* portable open format based on simple JSON/CSV files
* first user-created alphabets uploaded to [wop.mod.io] mod portal
* train Gaussian Mixture Models (GMM) from symbol data
* real-time symbol recognition
* spell language parser based of Parsing Expression Grammars (PEG)
* interfaces:
  * python module from [PyPI] (`texnomagic`)
  * Command-Line Interface (`texnomagic.cli`)
  * simple TCP server using JSON-RPC (`texnomagic.server`) - universal interface
* ⚠ format and API not stable yet
* ⚠ docs need more content


## Install

TexnoMagic is available from [PyPI]:

```
pip install texnomagic
```

You can install/develop from source as with any other python module.


## Use

### Python 🐍

See [reference docs] for `texnomagic` python module.

Use `tests/` and [python-wopeditor] as examples.

### CLI

`texnomagic` script should be installed, run it with `-h`/`--help` to get a
summary of options:

```
texnomagic -h
```

If your shell doesn't see the script (i.e. when not in `$PATH`), invoke the
`texnomagic.cli` module directly:

```
python -m texnomagic.cli list-abcs
```

### TexnoMagic JSON-RPC over TCP server

You can start universal language-agnostic TexnoMagic JSON-RPC over TCP server as
a python module:

```
python -m texnomagic.server
```

or compile a binary using PyInstaller:

```
pyinstaller server.spec
# results in dist/texnomagic-server
```

Simple reference python client is provided in `texnomagic.client` although it's
only used for testing in TexnoMagic.

For a full-fledged client implementation see [wopeditor].

### Godot Engine

[wopeditor] contains GDScript implementation of client for TexnoMagic
server (`texnomagic.server`).

You can use Godot's `JSONRPC` module to form requests and send them as strings
using standard Godot networking which TexnoMagic adpoted (messages prefixed with
4 bytes of total message length).

### GUI

[wopeditor] is a project dedicated to providing comprehensive GUI for
TexnoMagic.

## Bugs and Feature Requests

Please use [GitHub Issues](https://github.com/texnoforge/texnomagic/issues)
to report any problems or feature requests.

Contributions, suggestions, and ideas are always welcome ♥


## Contact

Feel free to drop by
[#wopeditor @ texnoforge discord](https://discord.gg/Dq3vaeg3pG).


[reference docs]: https://texnoforge.github.io/texnomagic/reference/texnomagic/
[wopeditor]: https://texnoforge.github.io/wopeditor/
[python-wopeditor]: https://texnoforge.github.io/python-wopeditor/
[PyPI]: https://pypi.org/project/texnomagic/
[wop.mod.io]: https://wop.mod.io
