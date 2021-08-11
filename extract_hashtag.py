import os, sys
import csv, json
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


def create_csv(file_name, path, d):
    with open(path, "w") as f:
        f.write(f"Name, Occurances, Positions" + "\n")
        for key,value in d.items():
            f.write(f"{key}, {value[0]}, " + f"{value[1]}".replace(",", ";") + "\n")
    print(f'The sorted hashtag occcurances list is contained in the file {path}.')
    return None


def plot_occurances(file_name, plots):
    base = os.path.splitext(file_name)[0]
    path = f"./{base}_sorted_hashtags.csv"
    if os.path.exists(path):
        print(f'The file {path} containing hashtag occurances already exists. If you would like to generate a plot, please delete the file {path} and re-run the script.')
        return 
    else:
        with open(file_name) as f:
            obj = json.load(f)
            l = len(obj)
            tags = get_hashtags(obj)
            tags = {key: (len(value), value) for (key, value) in tags.items()}
            sorted_tags = {k: v for k,v in sorted(tags.items(), key=lambda item: item[1], reverse=True)}
            create_csv(file_name, path, sorted_tags)
            k = list(sorted_tags.keys())
            v = list(sorted_tags.values())
            v = [i[0] for i in v]
            k = k[:plots]
            v = v[:plots]
            plt.scatter(k, v)
            plt.tight_layout()
            plt.title(f'Hashtag Distribution')
            plt.xlabel(f'Top {plots} hashtags from {l} posts.')
            plt.ylabel(f'Number of occurances')
            plt.show()
        return


if __name__ == "__main__":
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
            plot_occurances(sys.argv[1], int(sys.argv[2]))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
