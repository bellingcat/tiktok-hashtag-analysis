import logging
import argparse
from pathlib import Path
import sys

from .base import TikTokDownloader, load_hashtags_from_file


def create_parser():
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
        default=Path(".").resolve().parent / "data",
    )
    parser.add_argument("--log", type=str, help="File to write logs to", default=None)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
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

    downloader = TikTokDownloader(hashtags=hashtags, data_dir=args.output_dir)

    downloader.run(
        download=args.download, plot=args.plot, table=args.table, number=args.number
    )


if __name__ == "__main__":
    main()
