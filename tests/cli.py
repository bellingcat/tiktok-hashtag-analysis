import os
from pathlib import Path

import pytest

from tiktok_hashtag_analysis.cli import (
    create_parser,
    process_output_dir,
    DEFAULT_OUTPUT_DIR,
)

PARSER_ARGUMENTS = [
    ("file", "hashtags.txt", "--file"),
    ("download", True, "--download"),
    ("download", True, "-d"),
    ("number", 20, "--number"),
    ("plot", True, "--plot"),
    ("plot", True, "-p"),
    ("table", True, "--table"),
    ("table", True, "-t"),
    ("output_dir", "/tmp/tiktok_download", "--output-dir"),
    ("config", "~/.tiktok", "--config"),
    ("log", "../logfile.log", "--log"),
]


@pytest.mark.parametrize("attribute,value,flag", PARSER_ARGUMENTS)
def test_parser(hashtags, attribute, value, flag):
    argument_list = [*hashtags, flag]

    if not isinstance(value, bool):
        argument_list.append(str(value))

    parser = create_parser()
    args = vars(parser.parse_args(argument_list))

    assert args.get(attribute) == value
    assert args.get("hashtags") == hashtags


def test_process_output_dir(monkeypatch, tmp_path):

    home_dir = Path.home().resolve()

    # Specified nonexistent output directory without write permissions
    parser = create_parser()
    specified_output_dir = home_dir.parent / "test"
    with pytest.raises(SystemExit) as system_exit:
        result = process_output_dir(
            specified_output_dir=specified_output_dir, parser=parser
        )
    assert system_exit.type == SystemExit

    # Specified existing output directory without write permissions
    parser = create_parser()
    specified_output_dir = home_dir.parent
    with pytest.raises(SystemExit) as system_exit:
        result = process_output_dir(
            specified_output_dir=specified_output_dir, parser=parser
        )
    assert system_exit.type == SystemExit

    # Unspecified, in current directory without write permissions
    cwd = os.getcwd()
    monkeypatch.chdir(specified_output_dir)
    result = process_output_dir(specified_output_dir=None, parser=parser)
    monkeypatch.chdir(cwd)
    assert result == DEFAULT_OUTPUT_DIR

    # Specified nonexisting output directory with write permissions
    parser = create_parser()
    specified_output_dir = tmp_path / "test" / "tiktok"
    result = process_output_dir(
        specified_output_dir=specified_output_dir, parser=parser
    )
    assert result == specified_output_dir

    # Unspecified, in current directory with write permissions
    cwd = os.getcwd()
    monkeypatch.chdir(specified_output_dir)
    result = process_output_dir(specified_output_dir=None, parser=parser)
    monkeypatch.chdir(cwd)
    assert result == DEFAULT_OUTPUT_DIR
