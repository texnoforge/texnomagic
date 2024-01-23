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

**alpha**: integration with [wopeditor] and [wop.mod.io] mod portal

### Features

- save and load symbols to/from user files
- portable open format based on simple JSON/CSV files
- first user-created alphabets uploaded to [wop.mod.io] mod portal
- train Gaussian Mixture Models (GMM) from symbol data
- real-time symbol recognition
- spell language parser based of Parsing Expression Grammars (PEG)
- interfaces:
    - python module from [PyPI] (`texnomagic`)
    - Command-Line Interface (`texnomagic.cli`)
    - simple TCP server using JSON-RPC (`texnomagic.server`) - universal interface
- ⚠ format and API not stable yet
- ⚠ docs need more content


## Install

TexnoMagic is available from [PyPI] for Python **3.8+**,

Latest tested working Python version: **3.12**

```
pip install texnomagic
```

You can `install`/`develop` from source as with any other python module.


## Use

### GUI 🖱️

[wopeditor] is a project dedicated to providing comprehensive GUI for
TexnoMagic.

### CLI ⌨️

`texnomagic` script should be installed, run it without arguments to get a
summary of avaliable commands options:

```
$> texnomagic

Usage: texnomagic [OPTIONS] COMMAND [ARGS]...

  TexnoMagic CLI

Options:
  --version   Show TexnoMagic version and exit.
  -h, --help  Show this message and exit.

Commands:
  check-abcs     Check all/selected alphabets for issues.
  download-mods  Download Words of Power mods from wop.mod.io.
  flip-y         Flip Y axis for all symbols in alphabet.
  list-abcs      List all/selected TexnoMagic alphabets.
  list-mods      List online Words of Power mods from wop.mod.io.
  server         Start TexnoMagic TCP server on PORT.
  spell          Parse TexnoMagic spell.
  train-abcs     Train (missing) models for all/selected alphabets.
```

Add `-h`/`--help` after a command to get usage for that command:

```
$> texnomagic download-mods -h
```

If your shell doesn't see the script (i.e. when not in `$PATH`), you can invoke
the `texnomagic.cli` module directly:

```
$> python -m texnomagic.cli list-abcs --full
```

### Python 🐍

You can find code examples in:

* [tests/](https://github.com/texnoforge/texnomagic/tree/master/tests)
* [texnomagic/cli.py](https://github.com/texnoforge/texnomagic/blob/master/texnomagic/cli.py)
* [python-wopeditor](https://github.com/texnoforge/python-wopeditor/blob/master/wopeditor/wopeditor.py) (archived project)

See [reference docs] for `texnomagic` python module.

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


[reference docs]: https://texnoforge.github.io/texnomagic/reference/texnomagic/
[wopeditor]: https://texnoforge.github.io/wopeditor/
[texnomagic.client]: https://github.com/texnoforge/texnomagic/blob/master/texnomagic/client.py
[texnomagic.server]: https://github.com/texnoforge/texnomagic/blob/master/texnomagic/server.py
[wopeditor.client]: https://github.com/texnoforge/wopeditor/blob/master/texnomagic/client.gd
[PyPI]: https://pypi.org/project/texnomagic/
[wop.mod.io]: https://wop.mod.io
