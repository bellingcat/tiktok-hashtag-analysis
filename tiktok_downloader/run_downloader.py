import os, sys
import time
import json
import argparse, importlib

import global_data
import file_methods
import data_methods


"""
The run_downloader.py dowloads data using the tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper).
1. "-p" option is used by the user to download posts only
2. "-v" option is use to download videos only
3. "-p -v" is used to download posts and videos
4. "--h" is used to specify a list of hashtags as arguments
5. "-f" option is used to read the list of hashtags from the user specified file

Example:
    1. The command "python3 run_downloader.py --h london paris newyork -p" will download posts for hashtags london, paris and newyork.
    2. The command "python3 run_downloader.py -f hashtag_list -p -v" will download posts and videos for hashtags in the file hashtag_list.


The downloaded data is stored in the the data folder. The data is folder is organized as follows:
    1. the log subfolder contains the log.json that records total downloads (posts and videos) for each hashtag with a timestamp of when the script was run.
    2. the ids subfolder contains post_ids.json and video_ids.json that keep the record of post and video ids that are currently in the data set. This helps to filter out only new posts every time tiktok-scraper is run and only those new posts (or videos) are then stored in the data folder.
    3. Each hashtag has a subfolder by its name containing two subfolders, one each for posts and videos.


This scripts runs the function get_data in main which in turn triggers the following sequence:
    1. get_posts function is triggered if the user wants to download posts
    2. get_videos function is triggered if the user wants to download videos
    3. both functions above are sequentially triggered if the user wants to download both posts and videos.
    4. After the data is downloaded the log_writer is triggered to log the total number of posts and videos downloaded.


------------Files--------------
global_data - contains global constants relating to paths etc.
data_methods - this file contains data processing methods
file_methods - this file contains methods to write and update data in files
hashtag_list - this file contains the list of hashtags that the user wants to download data for.
"""


command = "python3 post_downloader.py "

def get_hashtag_list(file_name):
    try:
        f = importlib.import_module(file_name) # exec(f"from {file_name} import hashtag_list")
        print(f.hashtag_list)
        return f.hashtag_list
    except ImportError as error:
        print("ImportError: " + str(error))
        print(f"Please provide at least one hashtag either by entering as an argument or by adding hashtags to the variable hashtag_list in the file {file_name}")
        sys.exit()


def create_parser():
    # Creating the parser
    parser = argparse.ArgumentParser(description="Download the tiktoks for the requested hashtags")

    # Adding the arguments
    #parser.add_argument("--h", type=str, nargs="*", required=True, help="List of hashtags")
    parser.add_argument("--h", type=str, nargs="*", help="List of hashtags")
    parser.add_argument("-f", type=str, help="File name with the list of hashtags")
    parser.add_argument("-p", action="store_true", help="Download posts")
    parser.add_argument("-v", action="store_true", help="Download videos")

    return parser


def set_download_settings(download_data_type):
    """
    Loads the constants from global_data into the dict called settings and returns it.
    Purpose - easy access to global constants by various functions.
    """
    settings = {}
    settings["data"] = global_data.FILES["data"]
    settings["ids"] = global_data.FILES["ids"]
    settings["log"] = global_data.FILES["log"]
    settings["logger"] = global_data.FILES["logger"]
    settings["sleep"] = global_data.PARAMETERS["sleep"]
    settings["scraper"] = global_data.PARAMETERS["scraper_attempts"]
    file_methods.check_file(f"{settings['data']}/{settings['ids']}", "dir")
    file_methods.check_file(f"{settings['data']}/{settings['log']}", "dir")
    if download_data_type == "posts":
        settings["posts"] = global_data.FILES["posts"]
        settings["post_ids"] = global_data.FILES["post_ids"]
        settings["data_file"] = global_data.FILES["data_file"]
        return settings
    elif download_data_type == "videos":
        settings["videos"] = global_data.FILES["videos"]
        settings["video_ids"] = global_data.FILES["video_ids"]
        return settings
    elif download_data_type == "posts-videos":
        settings["posts"] = global_data.FILES["posts"]
        settings["post_ids"] = global_data.FILES["post_ids"]
        settings["data_file"] = global_data.FILES["data_file"]
        settings["videos"] = global_data.FILES["videos"]
        settings["video_ids"] = global_data.FILES["video_ids"]
        return settings
    else:
        print(f"ERROR: The download_data_type must be either posts, videos or posts-videos.")
        sys.exit()



def get_posts(settings, tag):
    """
    1. calls download_posts in file_methods.py to get the posts for a given hashtag
    2. calls extract_posts from data_methods.py to extract new posts if any
    3. calls update_posts from data_methods.py to update the id-list with the ids of newly downloaded posts.
    """
    file_path = file_methods.download_posts(settings, tag)
    log = ()
    if file_path:
        new_data = data_methods.extract_posts(settings, file_path, tag)
        if new_data:
            data_file = os.path.join(settings["data"], tag, settings["posts"], settings["data_file"])
            data_methods.update_posts(data_file, "file", new_data[1])
            log = data_methods.update_posts(settings["post_ids"], "file", new_data[0], tag)
        file_methods.delete_file(file_path, "file")

    return log



def get_videos(settings, tag):
    """
    1. calls download_videos in file_methods.py to get the videos for a given hashtag
    2. calls extract_videos from data_methods.py to extract new videos if any
    3. calls update_videos from data_methods.py to update the id-list with the ids of newly downloaded videos.
    4. the clean_video_files function deletes the residual video folder after the data processing
    """
    log = ()
    download_list = file_methods.download_videos(settings, tag)
    if download_list:
        new_data = data_methods.extract_videos(settings, tag, download_list)
        if new_data:
            log = data_methods.update_videos(settings, new_data, tag)
        else:
            file_methods.clean_video_files(settings, tag)

    return log



def get_data(hashtags, download_data_type):
    """
    The function checks for the user option "-p", "-v" or both and then
    triggers the functions get_posts, get_videos or both, respectively.
    """
    counter = 0
    total_hashtags = len(hashtags)
    total_hashtags_offset = total_hashtags - 1
    log_data = []

    if download_data_type == "posts":
        settings = set_download_settings(download_data_type)
        while counter < total_hashtags:
            tag = hashtags[counter]
            file_methods.check_file(os.path.join(settings["data"], tag, settings["posts"]), "dir")
            file_methods.check_file(os.path.join(settings["data"], tag, settings["posts"], settings["data_file"]), "file")
            res = get_posts(settings, tag)
            if res:
                log = ( res[0], ( "posts", res[1] ) )
                log_data.append(log)
                data_methods.print_total(settings["post_ids"], tag, download_data_type)

            counter += 1
            if counter < total_hashtags_offset:
                time.sleep(settings["sleep"])
    elif download_data_type == "videos":
        settings = set_download_settings(download_data_type)
        while counter < total_hashtags:
            tag = hashtags[counter]
            file_methods.check_file(os.path.join(settings["data"], tag, settings["videos"]), "dir")
            settings["videos_delete"] = settings['data'] + f"/{tag}/videos/#{tag}"
            settings["videos_to"] = settings['data'] + f"/{tag}/videos"
            res = get_videos(settings, tag)
            if res:
                res = ( res[0], ( "videos", res[1]))
                log_data.append(res)
                data_methods.print_total(settings["video_ids"], tag, download_data_type)

            counter += 1
            if counter < total_hashtags_offset:
                time.sleep(settings["sleep"])
    elif download_data_type == "posts-videos":
        settings = set_download_settings(download_data_type)
        while counter < total_hashtags:
            tag = hashtags[counter]
            file_methods.check_file(os.path.join(settings["data"], tag, settings["posts"]), "dir")
            file_methods.check_file(os.path.join(settings["data"], tag, settings["posts"], settings["data_file"]), "file")
            file_methods.check_file(os.path.join(settings["data"], tag, settings["videos"]), "dir")
            settings["videos_delete"] = settings['data'] + f"/{tag}/videos/#{tag}"
            settings["videos_to"] = settings['data'] + f"/{tag}/videos"
            requests = [("posts", "post_ids", get_posts), ("videos", "video_ids", get_videos)]
            total_reqs_offset = len(requests) - 1
            req_counter = 0
            for req in requests:
                res = req[2](settings, tag)
                if res:
                    res = ( res[0], (req[0], res[1]) )
                    log_data.append(res)
                    data_methods.print_total(settings[req[1]], tag, req[0])

                if req_counter < total_reqs_offset:
                    time.sleep(settings["sleep"])
                    req_counter += 1

            counter += 1
            if counter < total_hashtags_offset:
                time.sleep(settings["sleep"])
    else:
        print(f"ERROR: The download_data_type must be either posts, videos or posts-videos.")
        sys.exit()
    return log_data


def get_hashtags(file_name, hashtag_list):
    """
    Loads and returns the list of hashtags from user specified file.
    """
    try:
        from hashtag_list import hashtag_list
        return hashtag_list
    except:
        print(f"ERROR: something went wrong while reading the file {file_name}!")
        raise


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if not (args.h or args.f):
        parser.error("No hashtags were given, please use either --h option or -f to provide hashtags.")
        sys.exit()

    if not (args.p or args.v):
        parser.error("No argument given, please specify either -p for posts or -v videos or both.")
        sys.exit()

    if args.h:
        hashtags = args.h
    elif args.f:
        file_name = args.f
        hashtags = get_hashtag_list(file_name)

    print(hashtags)
    if not hashtags:
        print("No hashtags were given, please use either --h option or -f to provide hashtags.")
        sys.exit(0)

    if (args.p and args.v):
        download_data_type = "posts-videos"
    elif args.p:
        download_data_type = "posts"
    else:
        download_data_type = "videos"

    try:
        log_data = get_data(hashtags, download_data_type)
        if log_data:
            file_methods.log_writer(log_data)
    except:
        raise
