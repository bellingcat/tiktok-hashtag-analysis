import os, sys
import csv, json
import argparse
import matplotlib.pyplot as plt



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


def get_occurances(filename, n=1 , sort=True):
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



def plot(n, length, k, v):
    plt.scatter(k, v)
    plt.tight_layout()
    plt.title(f'Hashtag Distribution')
    plt.xlabel(f'Top {n} hashtags from {length} posts.')
    plt.ylabel(f'Number of occurances')
    plt.show()
    return


def print_occurances(k, v):
    row_number = 0
    print(f'Hashtag  Occurances')
    for key,value in zip(k, v):
        print(f'{row_number}\t{key}\t\t{value}')
        row_number += 1
    return



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="The json hashtag file name")
    parser.add_argument("n", help="The number of top n occurances", type=int)
    parser.add_argument("-p", "--plot", help="Plot the occurances", action="store_true")
    parser.add_argument("-d", "--print", help="List top n hashtags", action="store_true")
    args = parser.parse_args()
    if args.input_file and args.n:
        if args.n < 1:
            print(f"Please make sure the number of top occurances is a positive integer.")
            sys.exit()

        base = os.path.splitext(args.input_file)[0]
        path = f"./{base}_sorted_hashtags.csv"
        if args.plot:
            length, keys, values = get_occurances(args.input_file, args.n)
            plot(args.n, length, keys, values)
        else:
            length, keys, values = get_occurances(args.input_file, args.n)
            print_occurances(keys, values)
    else:
        print(f'ERROR: either {args.input_file} or {args.n} or both contains error.')
            
