import os, sys
import csv, json
import argparse
import matplotlib.pyplot as plt
<<<<<<< HEAD
from datetime import datetime

sys.path.insert(0, '../tiktok_downloader')
import file_methods, global_data
=======
>>>>>>> bfa90676f121dd88e070dc134791a596a104e784



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



<<<<<<< HEAD
def plot(n, length, k, v, img_folder):
    plt.scatter(k, v)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.title(f'Hashtag Distribution')
    plt.xlabel(f'Top {n} hashtags from {length} posts.')
    plt.ylabel(f'Number of occurrences')
    save_plot(plt, img_folder)
    plt.show(block=None)
=======
def plot(n, length, k, v):
    plt.scatter(k, v)
    plt.tight_layout()
    plt.title(f'Hashtag Distribution')
    plt.xlabel(f'Top {n} hashtags from {length} posts.')
    plt.ylabel(f'Number of occurrences')
    plt.show()
>>>>>>> bfa90676f121dd88e070dc134791a596a104e784
    return


def print_occurrences(l, k, v):
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


<<<<<<< HEAD
def save_plot(plt, img_folder):
    try:
        now = datetime.now()
        current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        plt.savefig(f"{img_folder}/{current_time}.png")

        return
    except: raise



if __name__ == "__main__":
    img_folder = global_data.IMAGES
    file_methods.check_file(img_folder, "dir")
=======

if __name__ == "__main__":
>>>>>>> bfa90676f121dd88e070dc134791a596a104e784
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
<<<<<<< HEAD
            plot(args.n, length, keys, values, img_folder)
=======
            plot(args.n, length, keys, values)
>>>>>>> bfa90676f121dd88e070dc134791a596a104e784
        else:
            length, keys, values = get_occurrences(args.input_file, args.n)
            print_occurrences(length, keys, values)
    else:
        print(f'ERROR: either {args.input_file} or {args.n} or both contains error.')
