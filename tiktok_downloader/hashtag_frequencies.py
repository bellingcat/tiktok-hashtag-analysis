import os
import json
import argparse
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", message="Glyph (.*) missing from current font")
import logging

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

sns.set_theme(style="darkgrid")

from file_methods import check_file, check_existence
from global_data import IMAGES

"""
Plots the frequency of hashtags appearing in the set of given posts.
"""


def get_hashtags(obj):
    if not obj:
        raise ValueError(f"Empty item, no hashtags to be extracted.")
    else:
        hashtags = {}
        tags = [[tag["name"] for tag in ele["hashtags"]] for ele in obj]
        tags = [set(ele) for ele in tags]
        {
            tag: (
                1
                if tag not in hashtags and not hashtags.update({tag: 1})
                else hashtags[tag] + 1 and not hashtags.update({tag: hashtags[tag] + 1})
            )
            for ele in tags
            for tag in ele
        }
        hashtags = sorted(hashtags.items(), key=lambda e: e[1], reverse=True)

        return hashtags


def get_occurrences(filename, n=1, sort=True):
    """
    Takes the json file containing posts and returns a dictionary:
    local variable occs = {
        "total": total posts in the file,
        top_n: [[top n hashtags ], [frequencies of corresponding hashtags]]
    }
    """
    with open(filename) as f:
        obj = json.load(f)
        l = len(obj)
        tags = get_hashtags(obj)
        occs = {"total": l, "top_n": []}
        occs["top_n"] = [[ele[i] for ele in tags[0:n]] for i in range(2)]
        return occs


def plot(n, occs, img_folder):
    y_pos = list(reversed(range(n - 1)))
    max_count = occs["top_n"][1][0]
    freqs = [count / max_count * 100 for count in occs["top_n"][1][1:]]
    labels = occs["top_n"][0][1:]

    fig, ax = plt.subplots(figsize=(5, 6.66))
    ax.barh(y_pos, freqs)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.grid(axis="y")
    ax.set_xlabel("Percent of posts with common hashtag")
    ax.set_ylim(min(y_pos) - 1, max(y_pos) + 1)
    ax.set_title(f'Common hashtags for #{occs["top_n"][0][0]} posts')
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    save_plot(img_folder)


def print_occurrences(occs):
    """
    Prints the top n hashtags with their frequencies and the ratio of occurrences and total posts, all to the shell.
    """
    row_number = 0
    total_posts = occs["total"]
    print(
        "{:<8} {:<15} {:<15} {:<15}".format(
            "Rank", "Hashtag", "Occurrences", "Frequency"
        )
    )
    for key, value in zip(occs["top_n"][0], occs["top_n"][1]):
        ratio = value / total_posts
        print("{:<8} {:<15} {:<15} {:<15}".format(row_number, key, value, ratio))
        row_number += 1


def save_plot(img_folder):
    """
    Saves the plot to a png file in the folder /data/imgs/
    """
    now = datetime.now()
    current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{img_folder}/{current_time}.png"
    logging.info(f"Plot saved to file: {filename}")
    plt.savefig(filename, bbox_inches="tight", facecolor="white", dpi=300)


def create_parser():
    """
    Creates the parser and the arguments for the user input.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="The json hashtag file name")
    parser.add_argument("n", help="The number of top n occurrences", type=int)
    parser.add_argument(
        "-p", "--plot", help="Plot the occurrences", action="store_true"
    )
    parser.add_argument(
        "-d", "--print", help="List top n hashtags", action="store_true"
    )
    return parser


if __name__ == "__main__":
    """
    Option "n" specifies how many hashtags does the user wants to plot.
    "-d" option prints the hashtag frequencies on the shell
    "-p" option plots the hashtag frequencies and saves as a png file in the folder /data/imgs/

    The function get_occurrences is triggered to compute and return the top n occurrences and the hashtags.
    """
    img_folder = IMAGES
    check_file(img_folder, "dir")
    parser = create_parser()
    args = parser.parse_args()
    if args.n < 1:
        raise ValueError(
            f"Specified argument `n` (the number of hashtags to analyze) must be greater than zero, not: {args.n}."
        )
    if not check_existence(args.input_file, "file"):
        raise FileNotFoundError(
            f"Specified argument `input_file` ({args.input_file}) does not exist."
        )
    base = os.path.splitext(args.input_file)[0]
    path = f"./{base}_sorted_hashtags.csv"
    occs = get_occurrences(args.input_file, args.n)
    if args.plot:
        plot(args.n, occs, img_folder)
    else:
        print_occurrences(occs)
