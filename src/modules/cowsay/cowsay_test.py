#!/usr/bin/env python
"""Automated tests for cowsay"""
import os

import pytest

import cowsay

SHELL_INJECTION = [
    "#test#; {injection} ##",
    "#test# | {injection} ##",
    "#test# `{injection}` ##",
    "#test# $({injection}) ##",
    "#test# && {injection} ##",
]

EXAMPLE_SAY = """\
 ______
< test >
 ------
        \   ^__^
         \  (**)\_______
            (__)\       )\/\\
             U  ||----w |
                ||     ||
"""

EXAMPLE_THINK = """\
 ______
( test )
 ------
         o
          o
            ^__^
    _______/($$)
/\/(       /(__)
   | W----|| |~|
   ||     || |~|  ~~
             |~|  ~
             |_| o
             |#|/
            _+#+_
"""

EXAMPLES = {
    'cowsay -e "**" -T "U " "test"': EXAMPLE_SAY,
    "cowthink -g -f bong -W 20 'test'": EXAMPLE_THINK,
}


@pytest.mark.parametrize('command', [
    "cowsay 'test'",
    'cowsay "test"',
] + ["cowsay -{} 'test'".format(flag) for flag in "bdgpstwy"] + [
    "cowsay -n 'test'",
    "cowsay -f cow 'test'",
    "cowsay -W 50 'test'",
    "cowsay -e '99' 'test'",
    'cowsay -e "99" "test"',
    "cowsay -T ' L' 'test'",
    'cowsay -T " L" "test"',
    "cowsay -W 30 -e ' o' 'test'",
    "cowsay -n -f cow 'test'",
    "cowsay -g -T 'U ' 'test'",
    'cowsay -e "**" -T "U " "test"',
])
def test_command_regex_success(command):
    """
    regex should match simple quoted string
    regex should match double quoted string
    regex should match preceding flags
    regex should match disable wrap
    regex should match cowmodel
    regex should match columns
    regex should match quoted eys
    regex should match quoted tongue
    regex should match combinations
    """

    assert cowsay.COMMAND_REGEX.match(command)


@pytest.mark.parametrize('command', [
    "cowsay test",
    "cowsay 'test",
    'cowsay "test',
    "cowsay -g",
    "cowsay -f cow",
])
def test_command_regex_failure(command):
    """
    regex should not match unquoted text
    regex should not match missing final quote
    regex should not match missing text
    """

    assert not cowsay.COMMAND_REGEX.match(command)


def test_command_regex_groups():
    """
    regex should produce cow and text groups
    """

    match = cowsay.COMMAND_REGEX.match("cowsay -f cow 'test'")
    groups = match.groupdict()
    text = groups.get('text')
    # [1:-1] is used to remove the first and the last character, that are
    # necessarly " or ', due to regex validation
    assert text and text[1:-1] == "test"
    cow = groups.get('cow')
    assert cow and cow == "cow"


@pytest.mark.parametrize('text', [
    inject.format(injection='malicious_command')
    for inject in SHELL_INJECTION
] + [
    "#test# > ~/.bashrc ##",
    "#test# < ~/.bashrc ##",
])
def test_command_regex_capture_injected_shell(text):
    """
    text group should ignore intermediate closing quotes
    """
    for quote in ('"', "'"):
        injection = text.replace('#', quote)
        command = "cowsay {}".format(injection)
        match = cowsay.COMMAND_REGEX.match(command)
        groups = match.groupdict()
        capture = groups.get('text')
        assert capture and capture == injection


@pytest.mark.parametrize('invalid_cow', ['pikachu', '"rm -f /"'])
def test_validate_cow_raise_unkown_cow(invalid_cow):
    """
    validate_cow should deny invalid cows
    """
    with pytest.raises(cowsay.UnkownCow):
        assert cowsay.validate_cow(invalid_cow)


@pytest.mark.parametrize('command,expected', EXAMPLES.items())
def test_invoke(command, expected):
    """
    invoke should perform without errors
    """
    result = cowsay.invoke(command)
    assert result
    removed_trailing_spaces = "\n".join([
        line.rstrip()
        for line in result.split("\n")
    ])
    assert removed_trailing_spaces == expected


@pytest.mark.parametrize('text', [
    inject.format(injection='touch malicious.txt')
    for inject in SHELL_INJECTION
])
def test_invoke_avoid_shell_injection(text, tmpdir):
    """
    invoke should not allow shell injection
    """
    os.chdir(str(tmpdir))
    for quote in ('"', "'"):
        injection = text.replace('#', quote)
        command = "cowsay {}".format(injection)
        assert cowsay.invoke(command)
        assert len(tmpdir.listdir()) == 0
