import os, sys
import csv, json
import re
from pandas import *

def arg_check():
    if len(sys.argv) != 3:
        print(f'ERROR: Please make sure you enter the following in the command line: python3 extract_posts.py file.json hashtag')
        sys.exit()
    else:
        return

def get_hashtag_positions(file_name, hashtag):
    base = os.path.splitext(file_name)[0]
    path = f"./{base}_sorted_hashtags.csv"
    if not os.path.exists(path):
        print(f'Generating {path} ...')
        os.system(f'python3 extract_hashtag.py {file_name} {1}')

    return tag_membership(hashtag, path)


def tag_membership(hashtag, path):
    data = read_csv(path)
    position_str = list(data[data["Name"] == hashtag].values[:, 2])
    if position_str:
        position_str = re.split('{|}', str(position_str))[1]
        p = position_str.replace(";", ",")
        positions = [int(s) for s in p.split(",")]
        return positions
    else:
        return


def print_posts(file_name, path, hashtag, positions):
    with open(file_name) as f:
        data = json.load(f)
        posts = []
        for p in positions:
            posts.append(data[p])
        keys = posts[0].keys()
        with open(path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, keys)
            writer.writeheader()
            writer.writerows(posts)
    print(f'The posts are contained in the file {path}.')
    return


if __name__ == "__main__":
    arg_check()
    file_name = sys.argv[1]
    hashtag = sys.argv[2]
    path = f"./{hashtag}_posts.csv"
    if os.path.exists(path):
        print(f'The file {path} containing hashtag occurances already exists. If you would like to run the script afresh, please delete the file {path} and re-run the script.')
        sys.exit()
    else:
        positions = get_hashtag_positions(file_name, hashtag)
        if positions:
            print_posts(file_name, path, hashtag, positions)
        else:
            print(f'{hashtag} not found!!!!')
            sys.exit()
