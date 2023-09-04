import pytest

from tiktok_hashtag_analysis.cli import create_parser

ARGUMENTS = [
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


@pytest.mark.parametrize("attribute,value,flag", ARGUMENTS)
def test_parser(hashtags, attribute, value, flag):
    argument_list = [*hashtags, flag]

    if not isinstance(value, bool):
        argument_list.append(str(value))

    parser = create_parser()
    args = vars(parser.parse_args(argument_list))

    assert args.get(attribute) == value
    assert args.get("hashtags") == hashtags
