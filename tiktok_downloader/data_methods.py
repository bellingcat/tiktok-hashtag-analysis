import os
from collections import namedtuple
from datetime import datetime
import global_data
import file_methods


Difference = namedtuple("Difference", "new_ids size")
Total = namedtuple("Total", "total unique")


def get_difference(tag, file, ids):
    maiden_entry = False
    current_id_data = file_methods.get_data(file)
    if tag in current_id_data:
        current_ids = current_id_data[tag]
        set1 = set(current_ids)
        set2 = set(ids)
        new_ids = set2.difference(set1)
        if new_ids:
            new_ids = list(new_ids)
            size = len(new_ids)
            diff = Difference(new_ids, size)
            return (diff, maiden_entry)
        else:
            return ([], maiden_entry)
    else:
        maiden_entry = True
        return (ids, maiden_entry)


def extract_posts(settings, file_name, tag):
    ids = []
    posts = []
    new_posts = []

    posts = file_methods.get_data(file_name)
    for post in posts:
        ids.append(post["id"])
    if not ids:
        print(f"WARNING: no posts were found for {tag} in the file - {file_name}")
        return
   
    status = file_methods.check_existence(settings["post_ids"], "file")
    if not status:
        new_data = (ids, posts)
        return new_data
    else:
        res = get_difference(tag, settings["post_ids"], ids)
        if res[1]:
            new_data = (ids, posts)
            return new_data
        else:
            if res[0]:
                for i in res[0].new_ids:
                    for post in posts:
                        if (i == post["id"]):
                            new_posts.append(post)
                new_data = (res[0].new_ids, new_posts)
                return new_data
            else:
                print(f"WARNING: No new posts were found in the downloaded file - {file_name}")
                return


def extract_videos(settings, tag, download_list):
    status = file_methods.check_existence(settings["video_ids"], "file")
    if not status:
        new_data = download_list
        return new_data
    else:
        res = get_difference(tag, settings["video_ids"], download_list)
        if res[1]:
            return download_list
        else:
            if res[0]:
                new_data = res[0].new_ids
                return new_data
            else:
                print(f"WARNING: No new videos were found for the {tag} in the downloaded folder.")
                return


def update_posts(file_path, file_type, new_data, tag=None):
    try:
        status = file_methods.check_existence(file_path, file_type)
        if not tag:
            file_methods.post_writer(file_path, new_data, status)
        else:
            log = file_methods.id_writer(file_path, new_data, tag, status)
            return log
    except:
        raise


def update_videos(settings, new_data, tag):
    file_path = settings["video_ids"]
    file_methods.check_file(file_path, "file")
    log = file_methods.id_writer(file_path, new_data, tag, True)
    file_methods.clean_video_files(settings, tag, new_data)
    return log


def get_total_posts(file_path, tag):
    status = file_methods.check_existence(file_path, "file")
    if not status:
        raise OSError("{file_path} not found!")
    else:
        data = file_methods.get_data(file_path)
        total = len(data[tag])
        unique = len(set(data[tag]))
        total = Total(total, unique)
        return total


def print_total(file_path, tag, data_type):
    total = get_total_posts(file_path, tag)
    if (total.total == total.unique):
        print(f"Total {data_type} for the hashtag {tag} are: {total.total}")
        return
    else:
        print(f"WARNING: out of total {data_type} for the hashtag {tag} {total.total}, only {total.unique} are unique. Something is going wrong...")
        return


