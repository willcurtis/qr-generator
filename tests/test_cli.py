from argparse import Namespace

from qr_generator.cli import build_parser, payload_from_args


def test_unquoted_sms_words_are_joined():
    args = build_parser().parse_args(["--sms", "12345", "hello", "there"])
    assert payload_from_args(args) == "SMSTO:12345:hello there"


def test_empty_text_reaches_validation():
    args = build_parser().parse_args(["--text", ""])
    assert isinstance(args, Namespace)
    assert args.text == ""
