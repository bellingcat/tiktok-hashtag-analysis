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
    ("limit", 1000, "--limit"),
    ("number", 20, "--number"),
    ("plot", True, "--plot"),
    ("plot", True, "-p"),
    ("table", True, "--table"),
    ("table", True, "-t"),
    ("verbose", True, "--verbose"),
    ("verbose", True, "-v"),
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


def test_output_dir_spec_noexist_nowrite(tmp_path):
    # Specified nonexistent output directory without write permissions
    parser = create_parser()
    os.chmod(tmp_path, 0o444)
    specified_output_dir = tmp_path / "test"
    with pytest.raises(SystemExit) as system_exit:
        result = process_output_dir(
            specified_output_dir=specified_output_dir, parser=parser
        )
    assert system_exit.type == SystemExit


def test_output_dir_spec_exist_nowrite(tmp_path):
    # Specified existing output directory without write permissions
    parser = create_parser()
    os.chmod(tmp_path, 0o444)
    specified_output_dir = tmp_path
    with pytest.raises(SystemExit) as system_exit:
        result = process_output_dir(
            specified_output_dir=specified_output_dir, parser=parser
        )
    assert system_exit.type == SystemExit


def test_output_dir_unspec_nowrite(monkeypatch, tmp_path):
    # Unspecified, in current directory without write permissions
    parser = create_parser()
    cwd = os.getcwd()
    specified_output_dir = tmp_path
    monkeypatch.chdir(specified_output_dir)
    os.chmod(tmp_path, 0o444)
    result = process_output_dir(specified_output_dir=None, parser=parser)
    monkeypatch.chdir(cwd)
    assert result == DEFAULT_OUTPUT_DIR


def test_output_dir_spec_noexist_write(tmp_path):
    # Specified nonexisting output directory with write permissions
    parser = create_parser()
    specified_output_dir = tmp_path / "test"
    result = process_output_dir(
        specified_output_dir=specified_output_dir, parser=parser
    )
    assert result == specified_output_dir


def test_output_dir_unspec_write(monkeypatch, tmp_path):
    # Unspecified, in current directory with write permissions
    parser = create_parser()
    cwd = os.getcwd()
    specified_output_dir = tmp_path
    monkeypatch.chdir(specified_output_dir)
    result = process_output_dir(specified_output_dir=None, parser=parser)
    monkeypatch.chdir(cwd)
    assert result == DEFAULT_OUTPUT_DIR
