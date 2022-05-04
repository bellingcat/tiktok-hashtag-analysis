import os, sys
import json
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
from file_methods import check_file
from global_data import IMAGES


"""
Plots the frequency of hashtags appearing in the set of given posts.
"""



def get_hashtags(obj):
    if not obj:
        print(f'ERROR: Empty item, no hashtags to be extracted.')
        return
    else:
        hashtags = {}
        tags = [ [tag['name'] for tag in ele['hashtags']] for ele in obj ]
        tags = [ set(ele) for ele in tags ]
        { tag: (1 if tag not in hashtags and not hashtags.update({tag: 1})
            else hashtags[tag] + 1 and not hashtags.update({tag: hashtags[tag] + 1})) 
            for ele in tags for tag in ele }
        hashtags = sorted(hashtags.items(), key=lambda e: e[1], reverse=True)

        return hashtags


def get_occurrences(filename, n=1 , sort=True):
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
        occs = {
                "total": l,
                "top_n": []
                }
        occs["top_n"] = [ [ ele[i] for ele in tags[0:n] ] for i in range(2)]
        return occs


def plot(n, occs, img_folder):
    plt.scatter(occs["top_n"][0], occs["top_n"][1])
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.title(f'Hashtag Distribution')
    plt.xlabel(f'Top {n} hashtags from {occs["total"]} posts.')
    plt.ylabel(f'Number of occurrences')
    save_plot(img_folder)
    plt.show(block=None)
    return


def print_occurrences(occs):
    """
    Prints the top n hashtags with their frequencies and the ratio of occurrences and total posts, all to the shell.
    """
    row_number = 0
    total_posts = occs["total"]
    print ("{:<8} {:<15} {:<15} {:<15}".format("Rank", 'Hashtag','Occurrences',f'Frequency (Occurrences/Total-Posts(total_posts))'))
    for key,value in zip(occs["top_n"][0], occs["top_n"][1]):
        ratio = value/total_posts 
        print ("{:<8} {:<15} {:<15} {:<15}".format(row_number, key, value, ratio))
        row_number += 1
    return


def save_plot(img_folder):
    """
    Saves the plot to a png file in the folder /data/imgs/
    """
    try:
        now = datetime.now()
        current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        plt.savefig(f"{img_folder}/{current_time}.png")

        return
    except: raise



if __name__ == "__main__":
    """
    Option "n" specifies how many hashtags does the user wants to plot.
    "-d" option prints the hashtag frequencies on the shell
    "-p" option plots the hashtag frequencies and saves as a png file in the folder /data/imgs/

    The function get_occurrences is triggered to compute and return the top n occurrences and the hashtags.
    """
    img_folder = IMAGES
    check_file(img_folder, "dir")
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="The json hashtag file name")
    parser.add_argument("n", help="The number of top n occurrences", type=int)
    parser.add_argument("-p", "--plot", help="Plot the occurrences", action="store_true")
    parser.add_argument("-d", "--print", help="List top n hashtags", action="store_true")
    args = parser.parse_args()
    if args.input_file and args.n:
        if args.n < 1:
            print(f"Please make sure the number of top occurrences is a positive integer.")
            sys.exit()

        base = os.path.splitext(args.input_file)[0]
        path = f"./{base}_sorted_hashtags.csv"
        occs = get_occurrences(args.input_file, args.n)
        if args.plot:
            plot(args.n, occs, img_folder)
        else:
            print_occurrences(occs)
    else:
        print(f'ERROR: either {args.input_file} or {args.n} or both contains error.')
