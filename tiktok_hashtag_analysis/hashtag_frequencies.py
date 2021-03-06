"""Analyze the frequency of hashtags appearing in the set of given posts.

- The "hashtag" positional argument specifies the hashtag of scraped posts to analyze
- The "n" positional argument specifies how many hashtags does the user wants to analyze
- Specifying the "-d" flag prints the hashtag frequencies on the shell
- Specifying the "-p" flag plots the hashtag frequencies and saves as a png file
"""

import os
import json
import argparse
from datetime import datetime
import warnings
from typing import List, Tuple, Dict, Any
import logging

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

from file_methods import check_file, check_existence
from global_data import IMAGES, FILES

warnings.filterwarnings("ignore", message="Glyph (.*) missing from current font")
sns.set_theme(style="darkgrid")
logger = logging.getLogger()


def create_parser() -> argparse.ArgumentParser:
    """Create the parser and the arguments for the user input."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "hashtag",
        type=str,
        help="The hashtag of scraped posts to analyze",
    )
    parser.add_argument("n", type=int, help="The number of top n occurrences")
    parser.add_argument(
        "-p", "--plot", help="Plot the occurrences", action="store_true"
    )
    parser.add_argument(
        "-d", "--print", help="List top n hashtags", action="store_true"
    )
    return parser


def get_hashtags(obj: Dict) -> List[Tuple[str, int]]:
    if not obj:
        raise ValueError(f"Empty item, no hashtags could be extracted.")
    else:
        hashtags = {}
        tags = [set([tag["name"] for tag in ele["hashtags"]]) for ele in obj]
        {
            tag: (
                1
                if tag not in hashtags and not hashtags.update({tag: 1})
                else hashtags[tag] + 1 and not hashtags.update({tag: hashtags[tag] + 1})
            )
            for ele in tags
            for tag in ele
        }

        return sorted(hashtags.items(), key=lambda e: e[1], reverse=True)


def get_occurrences(filename: str, n: int = 1) -> Dict[str, Any]:
    """Aggregate hashtag frequency information for a specified JSON file.

    Example: {
        "total": total posts in the file,
        top_n: [[top n hashtags ], [frequencies of corresponding hashtags]]
    }
    """
    with open(filename) as f:
        obj = json.load(f)
    l = len(obj)
    tags = get_hashtags(obj)
    occs = {"total": l, "top_n": []}
    occs["top_n"] = [[ele[i] for ele in tags[0 : min(l, n)]] for i in range(2)]
    return occs


def plot(occs: dict, img_folder: str):
    """Save plot of common hashtags as bar chart to file."""
    y_pos = list(reversed(range(len(occs["top_n"][0]) - 1)))
    max_count = occs["top_n"][1][0]
    freqs = [count / max_count * 100 for count in occs["top_n"][1][1:]]
    labels = occs["top_n"][0][1:]
    hashtag = occs["top_n"][0][0]

    fig, ax = plt.subplots(figsize=(5, 6.66))
    ax.barh(y_pos, freqs)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.grid(axis="y")
    ax.set_xlabel("Percent of posts with common hashtag")
    ax.set_ylim(min(y_pos) - 1, max(y_pos) + 1)
    ax.set_title(f"Common hashtags for #{hashtag} posts")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    save_plot(img_folder, hashtag)


def save_plot(img_folder, hashtag):
    """Save the plot as a png file in the folder ../data/imgs/"""
    now = datetime.now()
    current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{img_folder}/{hashtag}_{current_time}.png"
    logging.info(f"Plot saved to file: {filename}")
    plt.savefig(filename, bbox_inches="tight", facecolor="white", dpi=300)


def print_occurrences(occs):
    """Print information about the top n hashtags and their frequencies."""
    row_number = 0
    total_posts = occs["total"]
    print(
        "{:<8} {:<30} {:<15} {:<15}".format(
            "Rank", "Hashtag", "Occurrences", "Frequency"
        )
    )
    for key, value in zip(occs["top_n"][0], occs["top_n"][1]):
        ratio = value / total_posts
        print("{:<8} {:<30} {:<15} {:.4f}".format(row_number, key, value, ratio))
        row_number += 1
    print(f"Total posts: {total_posts}")


if __name__ == "__main__":

    img_folder = IMAGES
    check_file(img_folder, "dir")
    parser = create_parser()
    args = parser.parse_args()
    if args.n < 1:
        raise ValueError(
            f"Specified argument `n` (the number of hashtags to analyze) must be greater than zero, not: {args.n}."
        )
    input_file = data_file = os.path.join(
        FILES["data"], args.hashtag, FILES["posts"], FILES["data_file"]
    )
    if not check_existence(input_file, "file"):
        raise FileNotFoundError(
            f"File ({input_file}) for specified argument `hashtag` ({args.hashtag}) does not exist."
        )

    base = os.path.splitext(input_file)[0]
    path = f"./{base}_sorted_hashtags.csv"
    occs = get_occurrences(input_file, args.n)
    if args.plot:
        plot(occs, img_folder)
    else:
        print_occurrences(occs)
