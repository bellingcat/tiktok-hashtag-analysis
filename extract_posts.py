import os, sys
from extract_hashtag import get_occurances


def filter_positions(hashtags, keys, positions):
    filtered = []
    for hashtag in hashtags:
        try: 
            i = keys.index(hashtag)
            key = keys[i]
            post_indices = positions[i][1]
            filtered.append((key, post_indices))
        except Exception as error:
            print(error)
            continue
    return filtered


def write_posts(path, obj, filtered):
    length = len(filtered)
    with open(path, "w") as output_file:
        for i in range(length):
            hashtag = filtered[i][0]
            total_positions = len(filtered[i][1])
            positions = list(filtered[i][1])
            first_position = positions[0]
            output_file.write(f"{hashtag}, {obj[first_position]}" + "\n")
            for p in range(1, total_positions):
                output_file.write(f" , {obj[positions[p]]}" + "\n")
            print(f"{total_positions} posts written for the hashtag - {hashtag}")


if __name__ == "__main__":
    file_name = sys.argv[1]
    hashtags = list(sys.argv[2:])
    name = f"{hashtags[0]}_{len(hashtags)}"
    path = f"../{name}_posts.csv"
    if os.path.exists(path):
        print(f'The file {path} containing hashtag occurances already exists. If you would like to run the script afresh, please delete the file {path} and re-run the script.')
        sys.exit()
    else:
        obj, keys, positions = get_occurances(file_name, sort=False)
        filtered = filter_positions(hashtags, keys, positions)
        if filtered:
            write_posts(path, obj, filtered)
        else:
            print(f"No posts found for the hashtags you entered.")
        

