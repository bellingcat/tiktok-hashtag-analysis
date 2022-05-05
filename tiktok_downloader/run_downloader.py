import os
import time
import argparse
import logging, logging.config

import global_data
import file_methods
import data_methods


logging.config.fileConfig("../logging.config")
logger = logging.getLogger("Logger")


def get_hashtag_list(file_name: str) -> list:
    if not file_methods.check_existence(file_name, "file"):
        raise OSError(f"{file_name} does not exist")
    with open(file_name) as f:
        tags = list(
            filter(None, [line.strip() for line in f if not line.startswith("#")])
        )
        return tags


def create_parser():
    """
    Creates the parser and the arguments for the user input.
    """
    parser = argparse.ArgumentParser(
        description="Download the tiktoks for the requested hashtags"
    )

    parser.add_argument("-t", type=str, nargs="*", help="List of hashtags")
    parser.add_argument("-f", type=str, help="File name with the list of hashtags")
    parser.add_argument("-p", action="store_true", help="Download posts")
    parser.add_argument("-v", action="store_true", help="Download videos")

    return parser


def set_download_settings(download_data_type: str) -> dict:
    """
    Loads the constants from global_data into the dict called settings and returns it.
    Purpose - easy access to global constants by various functions.
    """
    settings = {}
    settings["data"] = global_data.FILES["data"]
    settings["ids"] = global_data.FILES["ids"]
    settings["sleep"] = global_data.PARAMETERS["sleep"]
    settings["scraper"] = global_data.PARAMETERS["scraper_attempts"]
    file_methods.check_file(f"{settings['data']}/{settings['ids']}", "dir")
    if download_data_type["posts"]:
        settings["posts"] = global_data.FILES["posts"]
        settings["post_ids"] = global_data.FILES["post_ids"]
        settings["data_file"] = global_data.FILES["data_file"]

    if download_data_type["videos"]:
        settings["videos"] = global_data.FILES["videos"]
        settings["video_ids"] = global_data.FILES["video_ids"]

    return settings


def get_posts(settings: dict, tag: str) -> tuple:
    """
    1. calls download_posts in file_methods.py to get the posts for a given hashtag
    2. calls extract_posts from data_methods.py to extract new posts if any
    3. calls update_posts from data_methods.py to update the id-list with the ids of newly downloaded posts.
    """
    file_path = file_methods.download_posts(settings, tag)
    number_scraped = ()
    if file_path:
        new_data = data_methods.extract_posts(settings, file_path, tag)
        if new_data:
            data_file = os.path.join(
                settings["data"], tag, settings["posts"], settings["data_file"]
            )
            data_methods.update_posts(data_file, "file", new_data[1])
            number_scraped = data_methods.update_posts(
                settings["post_ids"], "file", new_data[0], tag
            )
        file_methods.delete_file(file_path, "file")

    return number_scraped


def get_videos(settings: dict, tag: str) -> tuple:
    """
    1. calls download_videos in file_methods.py to get the videos for a given hashtag
    2. calls extract_videos from data_methods.py to extract new videos if any
    3. calls update_videos from data_methods.py to update the id-list with the ids of newly downloaded videos.
    4. the clean_video_files function deletes the residual video folder after the data processing
    """
    number_scraped = ()
    download_list = file_methods.download_videos(settings, tag)
    if download_list:
        new_data = data_methods.extract_videos(settings, tag, download_list)
        if new_data:
            number_scraped = data_methods.update_videos(settings, new_data, tag)
        else:
            file_methods.clean_video_files(settings, tag)

    return number_scraped


def get_data(hashtags: list, download_data_type: str) -> list:
    """
    The function checks for the user option "-p", "-v" or both and then
    triggers the functions get_posts, get_videos or both, respectively.
    """
    counter = 0
    total_hashtags = len(hashtags)
    total_hashtags_offset = total_hashtags - 1
    scraped_summary_list = []

    if download_data_type["posts"]:
        settings = set_download_settings(download_data_type)
        while counter < total_hashtags:
            tag = hashtags[counter]
            file_methods.check_file(
                os.path.join(settings["data"], tag, settings["posts"]), "dir"
            )
            file_methods.check_file(
                os.path.join(
                    settings["data"], tag, settings["posts"], settings["data_file"]
                ),
                "file",
            )
            res = get_posts(settings, tag)
            if res:
                number_scraped = (res[0], ("posts", res[1]))
                scraped_summary_list.append(number_scraped)
                data_methods.print_total(settings["post_ids"], tag, "posts")

            counter += 1
            if counter < total_hashtags_offset:
                time.sleep(settings["sleep"])

    if download_data_type["videos"]:
        settings = set_download_settings(download_data_type)
        while counter < total_hashtags:
            tag = hashtags[counter]
            file_methods.check_file(
                os.path.join(settings["data"], tag, settings["videos"]), "dir"
            )
            settings["videos_delete"] = settings["data"] + f"/{tag}/videos/#{tag}"
            settings["videos_to"] = settings["data"] + f"/{tag}/videos"
            res = get_videos(settings, tag)
            if res:
                res = (res[0], ("videos", res[1]))
                scraped_summary_list.append(res)
                data_methods.print_total(settings["video_ids"], tag, "videos")

            counter += 1
            if counter < total_hashtags_offset:
                time.sleep(settings["sleep"])

    return scraped_summary_list


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if not (args.t or args.f):
        parser.error(
            "No hashtags were given, please use either -t option or -f to provide hashtags."
        )

    if not (args.p or args.v):
        parser.error(
            "No argument given, please specify either -p for posts or -v videos or both."
        )

    if args.t:
        hashtags = args.t
    elif args.f:
        file_name = args.f
        hashtags = get_hashtag_list(file_name)

    logger.info(f"Hashtags to scrape: {hashtags}")
    if not hashtags:
        raise ValueError(
            "No hashtags were specified: please use either the -t flag to specify a sspace-separated list of one or more hashtags as a command-line argument, or use the -f flag to specify a text file of newline-separated hashtags."
        )

    download_data_type = {"posts": args.p, "videos": args.v}

    scraped_summary_list = get_data(hashtags, download_data_type)
    if scraped_summary_list:
        file_methods.log_writer(scraped_summary_list)
