import json
import os
from pathlib import Path, PurePosixPath
import random
import shutil

from texnomagic import common
from texnomagic.symbol import TexnoMagicSymbol
from texnomagic.drawing import TexnoMagicDrawing


INFO_FILE = 'texno_alphabet.json'


class TexnoMagicAlphabet:
    """
    TexnoMagic Alphabet is a set of [Symbols][texnomagic.symbol.TexnoMagicSymbol].

    Alphabet has:

    * `name`: arbitrary string
    * `path`: path to Alphabet dir
    * `symbols`: a set of Symbols

    This class provides convenient utilities for working with TexnoMagic Alphabets,
    see individual methods.
    """
    def __init__(self, path=None, name=None):
        if path and path.name.lower() == INFO_FILE:
            # accept path to alphabet info file as well
            path = path.parent

        self.path = path
        self.name = name
        self._symbols = None

    @property
    def info_path(self) -> Path:
        f"""Path to Alphabet `{INFO_FILE}` info file."""
        return self.path / INFO_FILE

    @property
    def symbols_path(self) -> Path:
        """Path to Alphabet `symbols` dir."""
        return self.path / 'symbols'

    @property
    def handle(self) -> str:
        """Alphabet handle (lowercase string)."""
        return common.name2handle(self.name)

    @property
    def symbols(self) -> list[TexnoMagicSymbol]:
        """A list of Symbols in `drawings` dir.

        Lazy loaded on-demand."""
        if self._symbols is None:
            self.load_symbols()
        return self._symbols

    def load(self, path=None):
        f"""Load Alphabet metadata from info file `{INFO_FILE}`."""
        if path:
            self.path = path

        assert self.path
        info = json.load(self.info_path.open())

        name = info.get('name')
        if not name:
            name = self.path.name
        self.name = name

        return self

    def load_symbols(self):
        """Load Symbols from `symbols` dir."""
        self._symbols = []
        for symbol_info_path in self.symbols_path.glob('*/texno_symbol.json'):
            symbol = TexnoMagicSymbol()
            symbol.load(symbol_info_path.parent)
            self._symbols.append(symbol)
        self.sort_symbols()

    def sort_symbols(self):
        """Sort symbols with common ordering."""
        if not self._symbols:
            return
        known = []
        for core_symbol in common.CORE_SYMBOLS_ORDER:
            for symbol in self._symbols:
                if symbol.meaning == core_symbol:
                    known.append(symbol)
                    self._symbols.remove(symbol)
                    break
        self._symbols = known + self._symbols

    def save(self):
        """Save the Alphabet into path."""
        os.makedirs(self.path, exist_ok=True)
        info = {
            'name': self.name,
        }
        return json.dump(info, self.info_path.open('w'))

    def save_new_symbol(self, symbol : TexnoMagicSymbol):
        """Save new Symbol into `symbols` dir."""
        assert symbol.name

        if self._symbols is None:
            self.load_symbols()

        symbol.path = self.symbols_path / common.name2fn(symbol.name)
        symbol.save()
        return self._symbols.insert(0, symbol)

    def export(self, out_path=None):
        """
        Export alphabet into a zipfile.
        """
        if not out_path:
            out_path = common.EXPORT_PATH

        ar_fn = self.path.name
        out_fn = out_path / ar_fn
        return shutil.make_archive(
            out_fn, 'zip',
            root_dir=self.path.parent,
            base_dir=self.path.name,
        )

    def normalize(self):
        """Normalize all Symbols. Overwrites files.

        See [texnomagic.drawing.TexnoMagicDrawing.normalize][]."""
        for s in self.symbols:
            s.normalize()

    def train_models(self, all : bool = False):
        """Train symbol models with available drawings.

        Train only missing models by default, use all to (re-)train all."""
        new, fail, old = [], [], []
        for symbol in self.symbols:
            if all or not symbol.model.ready:
                if symbol.model.train_symbol(symbol):
                    symbol.model.save()
                    new.append(symbol)
                else:
                    fail.append(symbol)
            else:
                old.append(symbol)
        return new, fail, old

    def calibrate(self):
        self.train_models(all=True)

    def scores(self, drawing : TexnoMagicDrawing, reverse : bool = True) -> list[tuple[TexnoMagicSymbol, float]]:
        """
        Score a Drawing using all Symbol models.

        Args:
            drawing: a Symbol Drawing to score
            reverse: reverse sorting order

        Returns:
            A list of (symbol, score) tuples ordered by score.
        """
        s = [(symbol, symbol.model.score(drawing)) for symbol in self.symbols]
        s = sorted(s, key=lambda x: x[1], reverse=reverse)
        return s

    def recognize(self, drawing : TexnoMagicDrawing) -> tuple[TexnoMagicSymbol | None, float]:
        """
        Recognize a Drawing within Alphabet Symbols.

        Args:
            drawing: a Symbol Drawing to recognize

        Returns:
            (symbol, score) tuple.
        """
        s = self.scores(drawing)
        if not s:
            return None, -1
        _symbol, score = s[0]
        if score < common.MIN_SCORE:
            return None, score
        return _symbol, score

    def check(self):
        """Check alphabet for problems."""
        # NOTE: This needs a rewrite into something less ugly.
        warns = dict()

        def log_warn(key, val=1.0):
            if key in warns:
                n, v = warns[key]
                warns[key] = (n + 1, (v * n + val) / (n + 1))
            else:
                warns[key] = (1, val)

        for symbol in self.symbols:
            if not symbol.model.ready:
                log_warn(('warn', 'missing_model', symbol), -1)
            if not symbol.get_image_path().exists():
                log_warn(('warn', 'missing_svg', symbol), -1)
            for drawing in symbol.drawings:
                scores = self.scores(drawing)
                rsymbol, rscore = scores[0]
                if rsymbol.meaning != symbol.meaning:
                    log_warn(('error', 'wrong_symbol', symbol, rsymbol), rscore)
                    prob = 'wrong_symbol'

                for rsy, rsc in scores[1:]:
                    # check scores for other symbols too
                    if rsc > 0.6:
                        lvl = 'warn'
                        if rsc > 0.8:
                            lvl = 'error'
                        log_warn((lvl,'high_score', symbol, rsy), rsc)

        results = {}
        for (level, prob, *args), (n, score) in warns.items():
            if prob == 'high_score':
                msg = "%s drawing got high score in %s: %s" % (args[0].meaning, args[1].meaning, score)
            elif prob == 'missing_model':
                msg = "%s symbol is missing model" % args[0].meaning
            elif prob == 'missing_svg':
                msg = "%s symbol is missing SVG image" % args[0].meaning
            else:
                msg = "%s drawing recognized as %s: %s" % (args[0].meaning, args[1].meaning, score)
            if n > 1:
                msg += "  (x%s)" % n
            if level not in results:
                results[level] = []
            results[level].append(msg)

        return results

    def get_symbol(self, name : str) -> TexnoMagicSymbol | None:
        """Get Symbol by name or meaning."""
        for s in self.symbols:
            if s.name == name or s.meaning == name:
                return s
        return None

    def random_symbol(self, exclude=None) -> TexnoMagicSymbol | None:
        """Get a random Symbol from the Alphabet."""
        if exclude:
            symbols = [s for s in self.symbols if s != exclude]
        else:
            symbols = self.symbols
        if len(symbols) < 1:
            return None
        return random.choice(symbols)

    def gen_readme_md(self, heading=3):
        """
        Generate Markdown for alphabet README.md
        """
        htxt = heading * '#'
        txt_ref = ''
        txt_body = ''
        for s in self.symbols:
            img_path = PurePosixPath().joinpath(*s.get_image_path().parts[-4:])
            stxt = (f"{htxt} {s}\n\n"
                    f"![{s}]({img_path})\n")
            if len(s.drawings) > 0:
                d_path = PurePosixPath().joinpath(*s.drawings_path.parts[-3:])
                stxt += f'\n{len(s.drawings)} [drawings]({d_path})\n'

            txt_ref += f"* [{s}](#{s.name}-{s.meaning.lower()})\n"
            txt_body += stxt + '\n'

        txt = f"**{len(self.symbols)}** symbols:\n\n{txt_ref}\n{txt_body}"
        return txt.rstrip()

    def as_dict(self, symbols=True) -> dict:
        """Return Alphabet as a dict."""
        d = {
            'name': self.name,
            'handle': self.handle,
            'path': str(self.path),
            'n_symbols': len(self.symbols),
        }
        if symbols:
            d['symbols'] = [s.meaning for s in self.symbols]
        return d

    def pretty(self, path=False):
        """Pretty Alphabet string with colors in rich formatting."""
        s = f'[cyan]{self.name}[/]: [white]{len(self.symbols)}[/] symbols'
        if path:
            s += f' @ [white]{self.path}[/]'
        return s

    def __str__(self):
        return f'{self.name}: {len(self.symbols)} symbols'

    def __repr__(self):
        return f"<TexnoMagicAlphabet: {self.__str__()}>"


def find_alphabet_at_path(path=None) -> TexnoMagicAlphabet:
    """Find Alphabet at path.

    When path is None, look at current path."""
    info = common.find_file_at_parents(INFO_FILE, path)
    if info:
        return TexnoMagicAlphabet(info)
    return None
