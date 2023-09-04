import pytest

from tiktok_hashtag_analysis.auth import Authorization

MS_TOKEN = "thisisafakemstokenfortiktok"


def test_auth_input(tmp_path, monkeypatch):
    config_file = tmp_path / ".tiktok"
    monkeypatch.setattr("builtins.input", lambda _: MS_TOKEN)
    auth = Authorization(config_file=config_file)
    auth.get_token()

    assert auth.ms_token == MS_TOKEN


def test_auth(tmp_path):
    config_file = tmp_path / ".tiktok"
    auth = Authorization(config_file=config_file)

    auth.dump_token(ms_token=MS_TOKEN)
    auth.get_token()

    assert auth.ms_token == MS_TOKEN
