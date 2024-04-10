# TexnoMagic Cookbook

A quick introduction to [TexnoMagic](index.md) Python module and CLI using examples.


## Where to put your Alphabets

Even though you can work with [Alphabets](abc.md) at any location, it's convenient to put them into expected paths where TexnoMagic looks by default.

You can view alphabets paths using CLI:

{{ "paths" | exec_cmd }}

It's recommended to use the `user` path for your Alphabets.

You can create and list `user` alphabets dir using CLI:

{{ "paths --abcs user --mkdir" | exec_cmd }}

Or open the dir using system file explorer:

```
texnomagic paths -a user -o
```

## Get an Alphabet (TexnoLatin)

We'll be working with [TexnoLatin] reference Alphabet in all the examples and
it's used for TexnoMagic testing as well.

Here's some `bash` to clone latest [TexnoLatin] into expected `user` path:

```bash
cd $(texnomagic paths --abcs user --mkdir)
git clone https://github.com/texnoforge/texnolatin/
```

Ensure the Alphabet is visible:

{{ 'abc list' | exec_cmd }}


## List Symbols from Alphabet

**CLI**:

{{ 'symbol list texnolatin' | exec_cmd }}

**Python**:

```python exec="true" source="material-block" result="ansi"
from texnomagic.cli_common import get_alphabet_or_fail

abc = get_alphabet_or_fail("texnolatin")
for symbol in abc.symbols:
	print(symbol)
```

## List Drawings of a Symbol

Use `ALPHABET:SYMBOL` syntax to select a specific [Symbol](symbol.md).

**CLI**:

{{ 'drawing list texnolatin/fire' | exec_cmd }}

**Python**:

```python exec="true" source="material-block" result="ansi"
from texnomagic.cli_common import get_alphabet_or_fail

abc = get_alphabet_or_fail("texnolatin")
symbol = abc.get_symbol("fire")
for drawing in symbol.drawings:
	drawing.load_curves()
	print(drawing)
```

[TexnoLatin]: https://github.com/texnoforge/texnolatin/
