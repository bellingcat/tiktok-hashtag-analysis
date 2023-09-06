from setuptools import setup


def read_requirements(filename: str):
    with open(filename) as requirements_file:
        import re

        def fix_url_dependencies(req: str) -> str:
            """Pip and setuptools disagree about how URL dependencies should be handled."""
            m = re.match(
                r"^(git\+)?(https|ssh)://(git@)?github\.com/([\w-]+)/(?P<name>[\w-]+)\.git",
                req,
            )
            if m is None:
                return req
            else:
                return f"{m.group('name')} @ {req}"

        requirements = []
        for line in requirements_file:
            line = line.strip()
            if line.startswith("#") or len(line) <= 0:
                continue
            requirements.append(fix_url_dependencies(line))
    return requirements


with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

# version.py defines the VERSION and VERSION_SHORT variables.
# We use exec here so we don't import cached_path whilst setting up.
VERSION = {}  # type: ignore
with open("tiktok_hashtag_analysis/version.py", "r") as version_file:
    exec(version_file.read(), VERSION)

setup(
    name="tiktok-hashtag-analysis",
    version=VERSION["VERSION"],
    author="Bellingcat",
    author_email="tech@bellingcat.com",
    packages=["tiktok_hashtag_analysis"],
    description="Analyze hashtags within posts scraped from TikTok",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bellingcat/tiktok-hashtag-analysis",
    license="MIT License",
    # install_requires=read_requirements("requirements.txt"),
    # extras_require={"dev": read_requirements("dev-requirements.txt")},
    install_requires=["seaborn", "matplotlib", "TikTokApi", "requests", "yt_dlp"],
    extras_require={"test": ["pytest", "pytest-cov", "pytest-html", "pytest-metadata"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": [
            "tiktok-hashtag-analysis=tiktok_hashtag_analysis.cli:main",
        ]
    },
)
