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


## Load Alphabet

It's recommended to access individual [Symbols](symbol.md) and
[Drawings](drawing.md) (data) through [TexnoMagicAlphabet](abc.md) class.


### Load Alphabet from standard paths

All further examples use `get_alphabet_or_fail` helper function to quickly get
`TexnoMagicAlphabet` instance from standard paths by name like this:

```python exec="true" source="material-block" result="ansi"
from texnomagic.cli_common import get_alphabet_or_fail

abc = get_alphabet_or_fail("texnolatin")

print(abc)
```

`get_alphabet_or_fail` is a convenience wrapper which auto-loads the Alphabet or
prints a pretty error message and exists when Alphabet isn't found.

See {{ 'texnomagic/cli_common.py' | file_link }} for details and inspiration.


### Load Alphabet from current dir

You can use `get_alphabet_or_fail` without `path` argument to look for an
Alphabet in current directory and its parents:

```python
from texnomagic.cli_common import get_alphabet_or_fail

abc = get_alphabet_or_fail()
```

Or you can use `find_alphabet_at_path` directly to search any path:

```python exec="true" source="material-block" result="ansi"
from pathlib import Path
from texnomagic.abc import find_alphabet_at_path

abc_path = Path('alphabets/texnolatin/symbols/fire')
abc = find_alphabet_at_path(abc_path)
abc.load()

print(abc)
```


### Load Alphabet from any path

You can load Alphabet directly by passing its `path` to [TexnoMagicAlphabet](abc.md) and calling `load` method:

```python exec="true" source="material-block" result="ansi"
from pathlib import Path
from texnomagic.abc import TexnoMagicAlphabet

abc_path = Path('alphabets/texnolatin')
abc = TexnoMagicAlphabet(path=abc_path)
abc.load()

print(abc)
```


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

## List Drawings of Symbol

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

## Render Drawing as a raster Image

You can render any [Drawing](drawing.md) into a `PIL.Image` for display or
further processing.

To display a Drawing in 200x200 pixels resolution:

**CLI**

```bash
texnomagic drawing render -r 200 alphabets/texnolatin/symbols/fire/drawings/fire_1709229865605.csv
```

**Python**:

```python exec="true" source="material-block" result="ansi"
from texnomagic.cli_common import get_alphabet_or_fail
from texnomagic.render import render_drawing

abc = get_alphabet_or_fail("texnolatin")
symbol = abc.get_symbol("friend")
drawing = symbol.random_drawing()
image = render_drawing(drawing, res=200)
print(image)
```

You can also display the image interactively:

```python
image.show()
```

Or save it to a PNG file:

```
image.save('fire.png')
```

You can also easily convert the image into `numpy.array` and do what you want
with it, for example use it to train neural networks using your own code:

```python exec="true" source="material-block" result="ansi"
import numpy as np

from texnomagic.cli_common import get_alphabet_or_fail
from texnomagic.render import render_drawing

abc = get_alphabet_or_fail("texnolatin")
symbol = abc.get_symbol("friend")
drawing = symbol.random_drawing()
image = render_drawing(drawing, res=16)
image_array = np.array(image)
print(f'Array shape: {image_array.shape}')
print(image_array)
```


[TexnoLatin]: https://github.com/texnoforge/texnolatin/
