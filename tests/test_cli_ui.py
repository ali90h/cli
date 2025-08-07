import os
import re
import shutil

import pytest

from tests.utils import http


# دالة مساعدة لإزالة الاقتباسات المفردة حول أسماء الخيارات، كي نتجنّب
# اختلاف إخراج Click/argparse بين الإصدارات المختلفة.
def _strip_quotes(msg: str) -> str:
    """Remove single quotes around option names."""
    return re.sub(r"'([a-z]+)'", r"\1", msg)


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


@pytest.fixture(scope="function")
def ignore_terminal_size(monkeypatch):
    """ثبت أبعاد الطرفية حتى لا يختلف التفاف النص أثناء الاختبارات."""
    monkeypatch.setitem(os.environ, "COLUMNS", str(PREDEFINED_TERMINAL_SIZE[0]))

    def fake_terminal_size(*_args, **_kwargs):
        return os.terminal_size(PREDEFINED_TERMINAL_SIZE)

    monkeypatch.setattr(shutil, "get_terminal_size", fake_terminal_size)
    monkeypatch.setattr(os, "get_terminal_size", fake_terminal_size)


@pytest.mark.parametrize(
    ("args", "expected_msg"),
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
