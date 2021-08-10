import os, sys
import csv, json
import matplotlib.pyplot as plt
from collections import Counter, OrderedDict


def get_hashtag_list(obj):
    if not obj:
        print(f'ERROR: Empty item, no hashtags to be extracted.')
        return
    else:
        hashtag_list = []
        length = len(obj)
        for i in range(length):
            for hashtag in obj[i]['hashtags']:
                hashtag_list.append(hashtag['name'])
    return hashtag_list


def create_csv(file_name, d):
    base = os.path.splitext(file_name)[0]
    path = f"./{base}_sorted_hashtags.csv"
    if os.path.exists(path):
        print(f'The file {path} containing hashtag occurances already exists.')
        return None
    else:
        with open(path, "w") as f:
            f.write(f"Name, Occurances" + "\n")
            for key,value in d.items():
                f.write(f"{key}, {value}" + "\n")
        print(f'The sorted hashtag occcurances list is contained in the file {path}.')
        return None


def plot_hashtag_occurances(file_name, plots):
    with open(file_name) as f:
        obj = json.load(f)
        length = len(obj)
        hashtag_list = get_hashtag_list(obj)
        hashtags = Counter(hashtag_list).most_common()
        hashtags_sorted = {k:v for (k,v) in hashtags}
        create_csv(file_name, hashtags_sorted)  
        k = list(hashtags_sorted.keys())
        v = list(hashtags_sorted.values()) 
        k = k[:plots]
        v = v[:plots]
        plt.scatter(k, v)
        plt.tight_layout()
        plt.title(f'Hashtag Distribution')
        plt.xlabel(f'Top {plots} hashtags from {length} posts.')
        plt.ylabel(f'Number of occurances')
        plt.show()
    return



if len(sys.argv) != 3:
    print(f'ERROR: Please make sure you enter the following in the command line: python3 file.json n. Where n is a positive integer value and will plot top n hashtags in the number of occurances.')
    sys.exit()
else:
    try:
        int(sys.argv[2])
    except:
        print(f'ERROR: Please make sure the number in the command line input: python3 file.json n, is a positive integer.')
        raise
    
    try:
        plot_hashtag_occurances(sys.argv[1], int(sys.argv[2]))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
