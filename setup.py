import setuptools
from tiktok_hashtag_analysis.version import __version__

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="tiktok-hashtag-analysis",
    version=__version__,
    author="Bellingcat",
    author_email="tech@bellingcat.com",
    packages=["tiktok_hashtag_analysis"],
    description="Analyze hashtags within posts scraped from TikTok",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bellingcat/tiktok-hashtag-analysis",
    license="MIT License",
    install_requires=["seaborn", "matplotlib"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3'
        ],
    entry_points={
        "console_scripts": [
            "tiktok_hashtag_analysis=tiktok_hashtag_analysis.__main__:main",
        ]
    },
)
