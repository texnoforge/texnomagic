"""
texnomagic exceptions

when texnomagic CLI run results in exception being raised
its returncode is returned as process return code
"""


class TexnoMagicException(Exception):
    returncode = 1


class InvalidUsage(TexnoMagicException):
    returncode = 10


class InvalidInput(TexnoMagicException):
    returncode = 11


class NotFound(TexnoMagicException):
    returncode = 30


class AlphabetNotFound(TexnoMagicException):
    returncode = 31
