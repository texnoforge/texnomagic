# TexnoMagic

**TexnoMagic** is a free and open source Python 3 library and format for magic
symbol recognition and symbol-based language parsing.

I created **TexnoMagic** after prototyping serveral systems for magic
symbol recognition and invocation as well as systems for creating magic
language based on symbols. You can read my posts about
[Theory of Magic](https://texnoforge.dev/words-of-power-devlog-1-theory-of-magic.html) and
[Invocation of Magic](https://texnoforge.dev/words-of-power-devlog-2-invocation-of-magic.html)
to get better idea of what I'm trying to achieve.


## Status

**alpha**: integration with [wopeditor]/Godot

* save and load symbols to/from user files
* portable open format based on simple JSON/CSV files
* first user-created alphabets uploaded to [wop.mod.io]
* train Gaussian Mixture Models (GMM) from symbol data
* real-time symbol recognition
* spell language parser based of Parsing Expression Grammars (PEG)
* available as python module or TCP server

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

### TexnoMagic TCP server

You can start language-agnostic TexnoMagic server as a python module:

```
python -m texnomagic.server
```

or compile a binary using PyInstaller:

```
pyinstaller server.spec
# results in dist/texnomagic-server
```

### Godot

[wopeditor] contains GDScript implementation of TCP client for TexnoMagic
server.


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
