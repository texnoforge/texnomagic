"""
Generate docs from texnomagic code/docstrings using mkdocs-macros-plugin.
"""
import subprocess

from pathlib import Path


BASE_PATH = Path(__file__).parent.parent
BASE_CODE_URL = "https://github.com/texnoforge/texnomagic/blob/master/"


def define_env(env):
    """
    This is available in docs using jinja2 templates.
    """
    # env.variables.exceptions = get_exceptions()

    @env.filter
    def relpath(path):
        return Path(path).relative_to(BASE_PATH)

    @env.filter
    def file_link(path):
        fn = Path(path)
        try:
            # full path can be passed (i.e. on Read the Docs)
            fn = Path(path).relative_to(BASE_PATH)
        except ValueError:
            pass
        return "[{fn}]({url}{fn})".format(
            fn=fn,
            url=BASE_CODE_URL)

    @env.filter
    def file_raw(path):
        return Path(path).open('r').read().strip()

    @env.filter
    def file_text(path):
        text = Path(path).open('r').read().strip()
        return "``` text\n%s\n```" % text

    @env.filter
    def mod_doc(modname):
        mod = __import__(modname, fromlist=[''])
        return mod.__doc__.strip()

    @env.filter
    def run(cmd):
        out = subprocess.getoutput(cmd)
        return "``` text\n$> %s\n\n%s\n```" % (
            cmd, out)

    @env.filter
    def exec_bash(cmd):
        return cmd

    @env.filter
    def exec_cmd(cmd):
        return (f'```bash\ntexnomagic {cmd}\n```\n'
                 '```bash exec="true" result="ansi"\n'
                f'texnomagic -C standard {cmd}\n```')

    @env.filter
    def cmd_help(cmd):
        c = 'texnomagic %s --help' % cmd
        return run(c)
