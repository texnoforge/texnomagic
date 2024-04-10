from rich.console import Console


console = Console()


def print(*args, **kwargs):
    return console.print(*args, **kwargs)


def log(*args, **kwargs):
    return console.log(*args, **kwargs)
