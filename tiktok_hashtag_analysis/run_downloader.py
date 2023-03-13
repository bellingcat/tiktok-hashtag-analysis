"""Download post data or videos from TikToks containing one or more specified hashtags.

- The "-p" flag specifies that only data from posts is downloaded, no video files
- The "-v" flag specifies that only video files are downloaded, no post data
- Specifying both "-p" and "-v" flags downloads both post data and video files
- The "-t" flag allows the user to specify a list of space-separated hashtags as an argument
- The "-f" flag allows the user to specify the filename of a text file containing a list of newline-separated hashtags as an argument
"""

import os
import time
from typing import List, Tuple, Dict, Any, Optional
from tempfile import TemporaryDirectory
from tiktok_hashtag_analysis import global_data
import tiktok_hashtag_analysis.file_methods as file_methods
from tiktok_hashtag_analysis import data_methods


def get_hashtag_list(file_name: str) -> List[str]:
    """Extract list of newline-separated hashtags from text file."""
    if not file_methods.check_existence(file_name, "file"):
        raise OSError(f"{file_name} does not exist")
    with open(file_name) as f:
        tags = list(
            filter(None, [line.strip() for line in f if not line.startswith("#")])
        )
        return tags


def set_download_settings(download_data_type: Dict[str, bool]) -> Dict[str, Any]:
    """Load the constants from global_data module into the `settings` dict."""
    settings = {
        "data": global_data.FILES["data"],
        "ids": global_data.FILES["ids"],
        "sleep": global_data.PARAMETERS["sleep"],
        "scraper": global_data.PARAMETERS["scraper_attempts"],
    }
    file_methods.check_file(f"{settings['data']}/{settings['ids']}", "dir")
    if download_data_type["posts"]:
        settings["posts"] = global_data.FILES["posts"]
        settings["post_ids"] = global_data.FILES["post_ids"]
        settings["data_file"] = global_data.FILES["data_file"]

    if download_data_type["videos"]:
        settings["videos"] = global_data.FILES["videos"]
        settings["video_ids"] = global_data.FILES["video_ids"]

    return settings


def get_posts(settings: dict, tag: str) -> Optional[Tuple[str, int]]:
    """Scrape trending TikTok post data for the specified hashtag.

    1. Calls `file_methods.download_posts` to scrape the post data for a given hashtag
    2. Calls `data_methods.extract_posts` to determine which if any posts
    haven't previously been downloaded.
    3. Calls `data_methods.update_posts` to update the ID list with the IDs of
    newly downloaded posts.
    """
    with TemporaryDirectory() as temp_dir:
        file_path = file_methods.download_posts(settings, tag, temp_dir)
        number_scraped = None
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

    return number_scraped


def get_videos(settings: dict, tag: str) -> Optional[Tuple[str, int]]:
    """Scrape trending TikTok video files for the specified hashtag.

    1. Calls `file_methods.download_videos` to download the video files for a given hashtag
    2. Calls `data_methods.extract_videos` to determine which if any videos
    haven't previouly been downloaded.
    3. Calls `data_methods.update_videos` to update the ID list with the IDs of
    newly downloaded videos.
    4. Calls `clean_video_files` function to delete the residual video folder
    after the data processing.
    """
    number_scraped = None
    download_list = file_methods.download_videos(settings, tag)
    if download_list:
        new_data = data_methods.extract_videos(settings, tag, download_list)
        if new_data:
            number_scraped = data_methods.update_videos(settings, new_data, tag)
        else:
            file_methods.clean_video_files(settings, tag)

    return number_scraped


def get_data(
        hashtags: list, download_data_type: Dict[str, bool]
) -> List[Tuple[str, Tuple[str, int]]]:
    """Check command-line arguments and scrape posts/videos for specified hashtags."""
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
            _res = get_videos(settings, tag)
            if _res:
                scraped_summary_list.append((_res[0], ("videos", _res[1])))
                data_methods.print_total(settings["video_ids"], tag, "videos")

            counter += 1
            if counter < total_hashtags_offset:
                time.sleep(settings["sleep"])

    return scraped_summary_list
