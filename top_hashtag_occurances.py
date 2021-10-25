#!/usr/bin/python3

import os, time
import json
import argparse
from datetime import datetime


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("hashtags", help="The hashtags to be processed", nargs="+")
    parser.add_argument("top_n", help="Top n occurances for a hashtag", type=int)
    args = parser.parse_args()
    return args


def check_file_existence(hashtag, contains=None):
    pwd = "./"
    for i in os.listdir(pwd):
        #if os.path.isfile(os.path.join(pwd, i)) and hashtag in i:
        if hashtag in i and contains in i:
            return i
        elif hashtag in i:
            return i
        else:
            continue
    return


def get_input_file(hashtag):
    check_file = check_file_existence(hashtag, "json")
    if check_file:
        return check_file
    else:
        try: 
            os.system(f"tiktok-scraper hashtag {hashtag} -t json")
            c = check_file_existence(hashtag, "json")
            if c:
                return c
            else:
                print(f"ERROR: No json file relating to {hashtag} found.")
        except:
            raise


def copy_data(input_file, output_file):
    os.system(f"cat {input_file} >> {output_file} && echo >> {output_file}")
    return


def get_data(hashtag, n):
    input_file = get_input_file(hashtag)
    if input_file:
        os.system(f"python3 extract_hashtag.py {input_file} {str(n)} -o")
        base = os.path.splitext(input_file)[0]
        data_file = f"{base}_sorted_hashtags.csv"
        if os.path.exists(data_file):
            return data_file
    return 


def get_occurances(hashtag, n, output):
    data_file = get_data(hashtag, n)
    copy_data(data_file, output)
    os.system(f"rm {data_file}")
    print(f"{data_file} removed ....")


if __name__ == "__main__":
    args = parser()
    hashtags = args.hashtags
    now = datetime.now().strftime("%d%m%Y-%H%M%S")
    output = f"./{now}.csv"
    l = len(hashtags)
    if l > 1:
        sleep = 30 # Sleep time (in secs) between two tiktok scraping requests.
        get_occurances(hashtags[0], args.top_n, output)
        for i in range(1, l):
            time.sleep(30)
            get_occurances(hashtags[i], args.top_n, output)
    else:
        get_occurances(hashtags[0], args.top_n, output)
    print(f"The output data is stored in the file {output}")
