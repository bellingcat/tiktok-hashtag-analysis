import os
import logging
import argparse
from pathlib import Path
from typing import Optional
from .base import TikTokDownloader, load_hashtags_from_file

DEFAULT_OUTPUT_DIR = Path.home() / "tiktok_hashtag_data"

logger = logging.getLogger(__name__)


def create_parser():
    """Create parser tp parse input command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Analyze hashtags within posts scraped from TikTok."
    )

    parser.add_argument(
        "hashtags",
        type=str,
        nargs="*",
        help="List of hashtags to scrape",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="File name containing list of hashtags to scrape",
    )
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Download video files corresponding to scraped posts",
    )
    parser.add_argument(
        "--number",
        type=int,
        help="The number of co-occurring hashtags to analyze",
        default=20,
    )
    parser.add_argument(
        "-p",
        "--plot",
        help="Plot the most common co-occurring hashtags",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--table",
        help="Print a table of the most common co-occurring hashtags",
        action="store_true",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save scraped data and visualizations to",
        default=None,
    )
    parser.add_argument(
        "--config",
        type=str,
        help="File name of configuration file to store TikTok credentials to",
        default=None,
    )
    parser.add_argument("--log", type=str, help="File to write logs to", default=None)
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of videos to download for each hashtag",
        default=1000,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "--headed",
        help="Don't use headless version of TikTok scraper",
        action="store_true",
    )
    return parser


def process_output_dir(
    specified_output_dir: Optional[str], parser: argparse.ArgumentParser
) -> Path:
    """Make sure the output directory can be created or has write permissions."""

    error_message = (
        lambda _output_dir: f"You don't have write permissions for the specified output directory (`{_output_dir}`). Please specify an output directory that you have write access to."
    )

    if specified_output_dir is None:
        return DEFAULT_OUTPUT_DIR
    else:
        _output_dir = Path(specified_output_dir).resolve()
        try:
            os.makedirs(_output_dir, exist_ok=True)
            if not os.access(path=_output_dir, mode=os.W_OK):
                parser.error(error_message(_output_dir))
            else:
                # On Windows, os.access is unreliable
                temp_file = _output_dir / "test.txt"
                with open(temp_file, "w") as f:
                    f.write("test")
                os.remove(temp_file)
                return _output_dir
        except PermissionError:
            parser.error(error_message(_output_dir))


def main():
    """Parse and process command-line arguments, scrape specified hashtags, and perform specified analyses."""

    parser = create_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        filename=args.log,
        format="%(asctime)s %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if len(args.hashtags) == 0:
        if not args.file:
            parser.error(
                "No hashtags were specified, please specify one or more hashtags "
                "to scrape or use the `--file` flag to specify a text file containing "
                "hashtags."
            )
        else:
            hashtags = load_hashtags_from_file(file=args.file)
    else:
        hashtags = args.hashtags

    output_dir = process_output_dir(specified_output_dir=args.output_dir, parser=parser)

    downloader = TikTokDownloader(
        hashtags=hashtags, data_dir=output_dir, config_file=args.config
    )

    downloader.run(
        limit=args.limit,
        download=args.download,
        plot=args.plot,
        table=args.table,
        number=args.number,
        headed=args.headed,
    )


if __name__ == "__main__":
    main()
