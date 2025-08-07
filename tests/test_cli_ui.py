import os
import re
import shutil
import pytest

from tests.utils import http

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _strip_quotes(msg: str) -> str:
    """
    Remove single quotes surrounding option names so the comparison works
    across different Click/argparse versions.
    """
    return re.sub(r"'([a-z]+)'", r"\1", msg)


# --------------------------------------------------------------------------- #
# Expected help messages                                                      #
# --------------------------------------------------------------------------- #
NAKED_BASE_TEMPLATE = """\
usage:
    http {extra_args}[METHOD] URL [REQUEST_ITEM ...]

error:
    {error_msg}

for more information:
    run 'http --help' or visit https://httpie.io/docs/cli

"""

NAKED_HELP_MESSAGE = NAKED_BASE_TEMPLATE.format(
    extra_args="",
    error_msg="the following arguments are required: URL",
)

NAKED_HELP_MESSAGE_PRETTY_WITH_NO_ARG = NAKED_BASE_TEMPLATE.format(
    extra_args="--pretty {all, colors, format, none} ",
    error_msg="argument --pretty: expected one argument",
)

NAKED_HELP_MESSAGE_PRETTY_WITH_INVALID_ARG = NAKED_BASE_TEMPLATE.format(
    extra_args="--pretty {all, colors, format, none} ",
    error_msg=(
        "argument --pretty: invalid choice: '$invalid' "
        "(choose from 'all', 'colors', 'format', 'none')"
    ),
)

PREDEFINED_TERMINAL_SIZE = (200, 100)

# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="function")
def ignore_terminal_size(monkeypatch):
    """
    Force a fixed terminal size so that wrapped output is deterministic.
    """

    def fake_terminal_size(*_args, **_kwargs):
        return os.terminal_size(PREDEFINED_TERMINAL_SIZE)

    # Python < 3.8 needs the COLUMNS env var
    monkeypatch.setitem(os.environ, "COLUMNS", str(PREDEFINED_TERMINAL_SIZE[0]))
    monkeypatch.setattr(shutil, "get_terminal_size", fake_terminal_size)
    monkeypatch.setattr(os, "get_terminal_size", fake_terminal_size)


# --------------------------------------------------------------------------- #
# Tests                                                                       #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "args, expected_msg",
    [
        ([], NAKED_HELP_MESSAGE),
        (["--pretty"], NAKED_HELP_MESSAGE_PRETTY_WITH_NO_ARG),
        (["pie.dev", "--pretty"], NAKED_HELP_MESSAGE_PRETTY_WITH_NO_ARG),
        (["--pretty", "$invalid"], NAKED_HELP_MESSAGE_PRETTY_WITH_INVALID_ARG),
    ],
)
def test_naked_invocation(ignore_terminal_size, args, expected_msg):
    result = http(*args, tolerate_error_exit_status=True)
    assert _strip_quotes(result.stderr) == _strip_quotes(expected_msg)
