#!/usr/bin/env python
"""Simulate linux cowsay commands"""

from glob import glob
from os import path
from shlex import quote  # python 3
from textwrap import dedent
import functools
import re
import subprocess

from telegram import ChatAction
from telegram.ext.dispatcher import run_async

TIMEOUT = 5
COWFILES = glob("/usr/local/share/cows/*.cow") + glob("/usr/share/cows/*.cow")
COWS = [path.splitext(path.basename(cow))[0] for cow in COWFILES]
COMMAND_REGEX = re.compile(
    r"^{cmd}{flag}?{disable_wrap}?{cow}?{columns}?{eyes}?{tongue}?{text}$"
        .format(
            cmd=r"(cow(?:say|think))",
            flag=r"(\s+-[bdgpstwy])",
            disable_wrap=r"(\s+-n)",
            cow=r"(\s+-f\s+(?P<cow>[^-][^\s]+))",
            columns=r"(\s+-W\s+\d+)",
            # force eyes, tongue and text quoting
            # (use longstrings to avoid " and ' escaping)
            eyes=r"""(\s+-e\s+(?P<eyes>[\'\"].{2}[\'\"]))""",
            tongue=r"""(\s+-T\s+(?P<tongue>[\'\"].{2}[\'\"]))""",
            text=r"""(\s+(?P<text>[\'\"].*[\'\"]))"""
        )
    # for the sake of simplicity, this regex enforce a specfic option order
    # unfortunatelly, this is not a desired behavior
)


class MalformedCommand(ValueError):
    pass


class UnkownCow(ValueError):
    pass


def help_command():
    """Usage for /cowsay command"""

    return (
        dedent(cowsay_command.__doc__) +
        "\nAvailable cows: {}.".format(", ".join(COWS))
    )


def generate_utils(bot, update):
    """\
    Simplify Telegram API usage by generating utility functions

    Arguments:
        bot - telegram bot object
        update - telegram update object

    Returns:
        tuple: ``reply`` and ``action`` functions
    """

    def reply(msg, **kwargs):
        """Send a text message"""
        return bot.sendMessage(
            text=msg, chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id, **kwargs)

    def action(kind, **kwargs):
        """Send a bot action of a given kind"""
        return bot.sendChatAction(
            chat_id=update.message.chat_id,
            action=getattr(ChatAction, kind), **kwargs)

    return (reply, action)


def validate_command(command):
    """Match the cowsay command using regular expression

    Security considerations:
        In order to avoid unexpected system calls, the command is
        matched against a regex, enforcing specific options and a
        well-defined format. After this validation, the only
        insecure arguments are COWMODEL, EYES, TONGUE and TEXT.

        COWMODEL needs to be validated against a specific list,
        EYES, TONGUE and TEXT need to be properly escaped.

    Arguments:
        command(str) - text to be validated

    Raises:
        MalformedCommand - if the command does not follow the command pattern

    Returns:
        Regex matching object.
        There are specific groups: ``cow``, ``eyes``, ``tongue``
        and ``text``.
    """
    match = COMMAND_REGEX.match(command)
    if not match:
        raise MalformedCommand

    return match


def validate_cow(cow):
    """Ensure the given cow is available

    Raises:
        UnkownCow - if the cowfile does not exist
    """

    if cow and cow not in COWS:
        raise UnkownCow

    return True


def invoke(command):
    """Invoke linux cowsay command using shell

    Arguments:
        command - string containing the cowsay command

    Raises:
        MalformedCommand - if the message does not follow the command pattern
        UnkownCow - if the cowfile does not exist
        subprocess.SubprocessError - if the command resulted in an error

    Returns:
        str - generated ASCII art
    """
    match = validate_command(command).groupdict()
    validate_cow(match.get("cow"))
    insecure = filter(None, [  # filter(None, ...) rejects empty elements
        match.get(group)
        for group in ("eyes", "tongue", "text")
    ])

    # quote properly to avoid shell injection:
    # [1:-1] is used to remove the first and the last character, that are
    # necessarly " or ', due to regex validation
    # shlex.quote is the python stdlib bullet-prof shell escape function
    escaped_command = functools.reduce(
        lambda cmd, txt: cmd.replace(txt, quote(txt[1:-1])),
        insecure,
        command
    )

    cow_process = subprocess.Popen(
        escaped_command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        cow_speech, err = cow_process.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        cow_process.kill()
        cow_speech, err = cow_process.communicate()

    if err:
        raise subprocess.SubprocessError(err)

    return cow_speech.decode("utf-8")


@run_async
def cowsay_command(bot, update, **kwargs):
    """\
    /cow{say|think} - ASCII art of a "cow" saying/thinking something.

    Usage:
    /cow{say|think} [-h] [-l] [-b | -d | -g | -p | -s | -t | -w | -y]
        [-n] [-f COWMODEL] [-W COLUMNS] [-e EYES] [-T TONGUE] [text]

    Arguments:
      text        what the cow says (within quotes)

    Options:
      -h, --help  show this help message and exit
      -l, --list  list all available cow models and exit
      -b          eyes are '==' (borg)
      -d          eyes are 'xx' and tongue is 'U ' (dead)
      -g          eyes are '$$' (greedy)
      -p          eyes are '@@' (paranoid)
      -s          eyes are '**' and tongue is 'U ' (stoned)
      -t          eyes are '--' (tired)
      -w          eyes are 'OO' (wired)
      -y          eyes are '..' (young)
      -n          disable word wrap, ignore -W, allowing FIGlet and ASCII art
      -f COWMODEL cow model to show
      -W COLUMNS  maximum width for the text within the balloon (default: 40)
      -e EYES     must be a quoted string of two characters
      -T TONGUE   must be a quoted string of two characters

    When using eyes/tongue flags, -e and -T will be ignored.
    """
    # help text borrowed from https://github.com/nicolalamacchia/pysay
    # so I think this specific text is licenced under
    # Apache License 2.0 (Apache-2.0) [https://www.tldrlegal.com/l/apache2]

    # get utils
    reply, action = generate_utils(bot, update)

    # Inform that the bot will send a text message
    action('TYPING')

    if any(flag in kwargs["args"] for flag in ("-h", "--help")):
        return reply(help_command())

    if any(flag in kwargs["args"] for flag in ("-l", "--list")):
        return reply(", ".join(COWS))

    try:
        # strip initial '/' and whitespace
        message = update.message.strip().lstrip('/')
        cow_speech = invoke(message)
    except MalformedCommand as ex:
        print(ex)
        return reply(
            "Ops, malformed message.\n"
            "Please consider the following information:\n\n---" +
            help_command())
    except UnkownCow as ex:
        print(ex)
        return reply(
            "Unkown cow. Please select one of: {}.".format(", ".join(COWS)))
    except subprocess.SubprocessError as ex:
        print(ex)
        reply("Ops, cowsay error.")

    # Markdown ``` allow monospaced fonts
    return reply("```\n{}\n```".format(cow_speech), parse_mode='Markdown')
