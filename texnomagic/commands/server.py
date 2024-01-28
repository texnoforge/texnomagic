import click


from texnomagic import server as server_

@click.command()
@click.argument('port', type=int, nargs=1, default=server_.DEFAULT_PORT)
def server(port):
    """
    Start TexnoMagic TCP server on PORT.
    """
    server_.serve(port=port)


TEXNOMAGIC_CLI_COMMANDS = [server]
