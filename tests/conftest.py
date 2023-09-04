import os
import tempfile

import pytest

TEST_HASHTAGS = ["embraceeuropa", "francisparkeryockey"]


@pytest.fixture(scope="package")
def hashtags():
    return TEST_HASHTAGS
