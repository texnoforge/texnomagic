from pathlib import Path

from texnomagic.abcs import TexnoMagicAlphabets


# pytest parametrization doesn't play well with fixtures,
# need to solve this on module-level :-/
BASE_PATH = Path(__file__).parents[1]
ABCS_PATH = BASE_PATH / 'alphabets'
assert ABCS_PATH.exists()
ABCS = TexnoMagicAlphabets({'test': ABCS_PATH})
ABCS.load()
ABC = ABCS.abcs['test'][0]
N_SYMBOLS = len(ABC.symbols)
