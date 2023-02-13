"""Utility functions that operate on files, such as writing to reading from a file.
"""

import os
import json
import subprocess
from os import path
from datetime import datetime
import shutil
from typing import Tuple, List, Optional, Dict, Any

import logging, logging.config

logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), 'logging.config'))
logger = logging.getLogger("Logger")


def create_file(name: str, file_type: str):
    """Create a file or directory."""
    if file_type == "dir":
        os.makedirs(name, mode=0o777)
    elif file_type == "file":
        with open(name, "w"):
            pass
    else:
        raise ValueError(f"{file_type} has to be either 'dir' or 'file'")


def check_existence(file_path: str, file_type: str):
    """Check if a file or a directory exists."""
    if file_type == "file":
        return os.path.isfile(file_path)
    elif file_type == "dir":
        return os.path.isdir(file_path)
    else:
        raise ValueError(f"{file_type} has to be either 'dir' or 'file'")


def check_file(file_path: str, file_type: str):
    """If path does not exist, creates a file or directory."""
    status = check_existence(file_path, file_type)
    if not status:
        create_file(file_path, file_type)


def download_posts(settings: Dict, tag: str, output_dir: Any):
    """Run the tiktok-scraper command to download posts for a given hashtag.

    Returns the path to the downloaded file of posts. If no file was downloaded,
    prints the error and returns nothing in order to move on.

    os.chdir is used to execute shell commands in the correct folder and then
    reused to return to the original folder of execution of run_downloader script.
    """
    path = os.path.join(settings["data"], tag, settings["posts"])
    os.makedirs(path, exist_ok=True)
    tiktok_command = f"tiktok-scraper hashtag {tag} -t 'json' --filepath {output_dir}"
    output = subprocess.check_output(tiktok_command, shell=True, encoding="utf-8")
    new_file = output.split()[-1]
    if "json" in new_file:
        return new_file
    else:
        logger.warn(
            f"Something's wrong with what is returned by tiktok-scraper for the hashtag {tag} - *{new_file}* is not a json file.\n\ntiktok-scraper returned {output}"
        )


def download_videos(settings: Dict, tag: str):
    """Run the tiktok-scraper command to download videos for a given hashtag.

    Note that all the videos are downloaded that are returned by the TikTok API,
    making this a time- and data-intensive process.
    The list of downloaded video IDs is constucted and returned if the
    downloaded folder contains at least 1 video.

    os.chdir is used to execute shell commands in the correct folder and then
    reused to return to the original folder of execution of run_downloader script.
    """
    path = os.path.join(settings["data"], tag, settings["videos"])
    os.makedirs(path, exist_ok=True)
    tiktok_command = f"tiktok-scraper hashtag {tag} -d --filepath {path}"
    result = subprocess.check_output(tiktok_command, shell=True)
    downloaded_list_tmp = os.listdir(os.path.join(path, f"#{tag}"))
    if downloaded_list_tmp:
        downloaded_list = []
        for file in downloaded_list_tmp:
            file = file.split(".")[0]
            downloaded_list.append(file)

        return downloaded_list
    else:
        logger.warn(f"No video files were downloaded for the hashtag {tag}.")
        shutil.rmtree(settings["videos_delete"])


def get_data(file_path: str) -> Any:
    """Read a JSON file and return the read data."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def dump_data(file_path: str, data: Any):
    """Write data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def log_writer(log_data: List[Tuple[str, Tuple[str, int]]]):
    """Create the dictionary of total downloads (posts and videos) per hashtag.

    Example : {
        timetamp : {
            hashtag : {
                videos : number_of_new_videos ,
                posts : number_of_new_posts
            }
        }
    }

    Writes the dictionary to the log file (`logs/log.json`).
    """

    total = 0
    scraped_summary_dict = {}  # type: Dict[str, Dict[str, int]]
    for hashtag, (data_type, count) in log_data:
        if hashtag in scraped_summary_dict:
            if data_type in scraped_summary_dict[hashtag]:
                scraped_summary_dict[hashtag][data_type] += count
            else:
                scraped_summary_dict[hashtag][data_type] = count
            total += count
        else:
            scraped_summary_dict[hashtag] = {data_type: count}
            total += count

    now_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    data = {now_str: scraped_summary_dict}

    logger.debug(f"Logged post data: {data}")
    logger.info(f"Successfully scraped {total} total entries")


def id_writer(
    file_path: str, new_data: List[str], tag: str, status: bool
) -> Tuple[str, int]:
    """Write the list of new ids to the post_ids or video_ids file."""

    total = len(new_data)
    if status:
        try:
            data = get_data(file_path)
            if tag in data:
                data[tag] += new_data
            else:
                data[tag] = new_data
            dump_data(file_path, data)
        except json.decoder.JSONDecodeError:
            data = {tag: new_data}
            dump_data(file_path, data)
    else:
        data = {tag: new_data}
        dump_data(file_path, data)
    logger.debug(f"SUCCESS - {total} entries added to {file_path}")
    number_scraped = (tag, total)
    return number_scraped


def post_writer(file_path: str, new_data: List[Dict], status: bool):
    """Write the new posts in the post file of the given hashtag
    (`/data/{hashtag}/posts/data.json`).
    """
    total = len(new_data)
    if status:
        try:
            data = get_data(file_path)
            data += new_data
            dump_data(file_path, data)
        except json.decoder.JSONDecodeError:
            data = new_data
            dump_data(file_path, data)
    else:
        data = new_data
        dump_data(file_path, data)
    logger.debug(f"SUCCESS - {total} entries added to {file_path}")


def delete_file(file_path: str, file_type: str):
    """Delete a directory or file."""
    if not check_existence(file_path, file_type):
        raise OSError(f"Attempt to delete file failed: {file_path} does not exist")
    elif file_type == "file":
        os.remove(file_path)
        logger.debug(f"Successfully deleted {file_path}")
    elif file_type == "dir":
        os.rmdir(file_path)
        logger.debug(f"Successfully deleted {file_path}")
    else:
        raise OSError("{file_type} needs to be either 'file' or 'dir'")


def clean_video_files(settings: dict, tag: str, new_data: Optional[List[str]] = None):
    """Move the new videos from the tiktok-scraper video folder to `/data/{hashtag}/videos/`.
    Deletes the residual tiktok-scraper video folder.
    """
    if new_data:
        for file in new_data:
            settings["videos_from"] = (
                settings["data"] + f"/{tag}/videos/#{tag}/{file}.mp4"
            )
            shutil.move(settings["videos_from"], settings["videos_to"])

    shutil.rmtree(settings["videos_delete"])
    logger.debug(
        f"Successfully deleted the folder {settings['videos_delete']} folder of videos."
    )
