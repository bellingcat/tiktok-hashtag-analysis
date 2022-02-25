import os, sys
import csv, json
import argparse
import matplotlib.pyplot as plt
from datetime import datetime

"""
Plots the frequency of hashtags appearing in the set of given posts.
"""


sys.path.insert(0, '../tiktok_downloader')
import file_methods, global_data



def get_hashtags(obj):
    if not obj:
        print(f'ERROR: Empty item, no hashtags to be extracted.')
        return
    else:
        hashtags = {}
        l = len(obj)
        for i in range(l):
            for hashtag in obj[i]['hashtags']:
                if hashtag['name'] in hashtags:
                    hashtags[hashtag['name']].add(i)
                else:
                    hashtags[hashtag['name']] = {i}
    return hashtags


def get_occurrences(filename, n=1 , sort=True):
    """
    Takes the json file containing posts and returns the triplet:
    l : total posts in the file
    k : list of top n hashtags
    v_total : frequency of top n hashtags in l
    """
    with open(filename) as f:
        obj = json.load(f)
        l = len(obj)
        tags = get_hashtags(obj)
        tags = {key: (len(value), value) for (key, value) in tags.items()}
        if not sort:
            k = list(tags.keys())
            v = list(tags.values())
            return obj, k, v
        else:
            sorted_tags = {k: v for k,v in sorted(tags.items(), key=lambda item: item[1], reverse=True)}
            k = list(sorted_tags.keys())
            v = list(sorted_tags.values())
            k = k[:n]
            v_total = [i[0] for i in v]
            v_total = v_total[:n]
            return l, k, v_total



def plot(n, length, k, v, img_folder):
    plt.scatter(k, v)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.title(f'Hashtag Distribution')
    plt.xlabel(f'Top {n} hashtags from {length} posts.')
    plt.ylabel(f'Number of occurrences')
    save_plot(plt, img_folder)
    plt.show(block=None)
    return


def print_occurrences(l, k, v):
    """
    Prints the top n hashtags with their frequencies and the ratio of occurrences and total posts, all to the shell.
    """
    row_number = 0
    total_posts = l
    print ("{:<8} {:<15} {:<15} {:<15}".format("Rank", 'Hashtag','Occurrences',f'Frequency (Occurrences/Total-Posts({l}))'))
    #print(f'Hashtag                  Occurrences                 Frequency(Occurances/Total-Posts)')
    for key,value in zip(k, v):
        ratio = value/total_posts
        print ("{:<8} {:<15} {:<15} {:<15}".format(row_number, key, value, ratio))
        #print(f'{row_number}\t{key}\t\t{value}\t\t{ratio:.3f}')
        row_number += 1
    return


def save_plot(plt, img_folder):
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

    The function get_occurances is triggered to compute and return the top n occurances and the hashtags.
    """
    img_folder = global_data.IMAGES
    file_methods.check_file(img_folder, "dir")
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
        if args.plot:
            length, keys, values = get_occurrences(args.input_file, args.n)
            plot(args.n, length, keys, values, img_folder)
        else:
            length, keys, values = get_occurrences(args.input_file, args.n)
            print_occurrences(length, keys, values)
    else:
        print(f'ERROR: either {args.input_file} or {args.n} or both contains error.')
