"""Utility functions that perform data processing related tasks.
"""

from typing import NamedTuple, List, Tuple, Set, Optional, Dict, Any
import logging

from . import file_methods

logger = logging.getLogger()


class Diff(NamedTuple):
    """Keep track of scraped post IDs and whether previously-scraped posts have been filtered."""

    ids: Set[str]
    filter_posts: bool


class Total(NamedTuple):
    """Keep track of number of total and number of unique scraped posts."""

    total: int
    unique: int


def get_difference(tag: str, file_name: str, ids: List[str]) -> Optional[Diff]:
    """Find TikTok post IDs that haven't previously been scraped.

    Filter out the new posts for the hashtag `tag` by comparing the list of
    post IDs contained in `filename` to the list of newly downloaded IDs
    contained in `ids`.
    """
    filter_posts = False
    current_id_data = file_methods.get_data(file_name)
    if tag in current_id_data:
        current_ids = current_id_data[tag]
        set_current_ids = set(current_ids)
        total_current_ids = len(set_current_ids)
        set_ids = set(ids)
        new_ids = set_ids.difference(set_current_ids)
        if not new_ids:
            return None
        else:
            total_new_ids = len(new_ids)
            if total_new_ids == total_current_ids:
                new_data = Diff(new_ids, filter_posts)
            else:
                new_data = Diff(new_ids, filter_posts)
            return new_data
    else:
        filter_posts = True
        new_data = Diff(set(ids), filter_posts)
        return new_data


def extract_posts(
    settings: Dict[Any, Any], file_name: str, tag: str
) -> Optional[Tuple[List[str], List[Dict]]]:
    """Find TikTok posts that haven't previously been scraped.

    Compares the file downloaded by tiktok-scraper to the list of
    previously-scraped posts (from the file ids/post_ids.json).
    """
    ids = []
    posts = []

    posts = file_methods.get_data(file_name)
    for post in posts:
        ids.append(post["id"])

    if not ids:
        logger.warn(f"No posts were found for the hashtag: {tag}")
        return None

    status = file_methods.check_existence(settings["post_ids"], "file")
    if not status:
        new_data = (ids, posts)
        return new_data
    else:
        new_ids = get_difference(tag, settings["post_ids"], ids)
        if not new_ids:
            logger.warn(f"No new posts were found for the hashtag: {tag}")
            return None
        elif new_ids.filter_posts:
            new_posts = [post for post in posts if post["id"] in new_ids.ids]
            return (list(new_ids.ids), new_posts)
        else:
            return (list(new_ids.ids), posts)


def extract_videos(settings: dict, tag: str, download_list: List[str]) -> List[str]:
    """Find TikTok videos that haven't previously been scraped.

    Compares the file downloaded by tiktok-scraper to the list of
    previously-scraped videos (from the file ids/video_ids.json).
    """
    status = file_methods.check_existence(settings["video_ids"], "file")
    if not status:
        new_data = download_list
        return new_data
    else:
        new_videos = get_difference(tag, settings["video_ids"], download_list)
        if not new_videos:
            logger.warn(
                f"No new videos were found for the {tag} in the downloaded folder."
            )
            return []
        else:
            return list(new_videos.ids)


def update_posts(
    file_path: str, file_type: str, new_data: List[Any], tag: str = None
) -> Optional[Tuple[str, int]]:
    """Update the file containing scraped post IDs (`ids/post_ids.json`) with
    the IDs of the recently scraped posts.
    """
    status = file_methods.check_existence(file_path, file_type)
    if not tag:
        file_methods.post_writer(file_path, new_data, status)
        return None
    else:
        scraped_data = file_methods.id_writer(file_path, new_data, tag, status)
        return scraped_data


def update_videos(
    settings: Dict[str, Any], new_data: List[str], tag: str
) -> Tuple[str, int]:
    """Update the file containing video IDs (`ids/video_ids.json`) with the IDs
    of the recently scraped videos.
    """
    file_path = settings["video_ids"]
    file_methods.check_file(file_path, "file")
    number_scraped = file_methods.id_writer(file_path, new_data, tag, True)
    file_methods.clean_video_files(settings, tag, new_data)
    return number_scraped


def get_total_posts(file_path: str, tag: str) -> Total:
    """Count number of total scraped posts and number of unique scraped posts."""
    status = file_methods.check_existence(file_path, "file")
    if not status:
        raise OSError(f"{file_path} not found!")
    else:
        data = file_methods.get_data(file_path)
        total_posts = len(data[tag])
        unique = len(set(data[tag]))
        t = Total(total_posts, unique)
        return t


def print_total(file_path: str, tag: str, data_type: str):
    """Print number of total and unique scraped posts, warn if any non-unique posts."""
    total = get_total_posts(file_path, tag)
    if total.total == total.unique:
        logger.info(f"Scraped {total.total} {data_type} containing the hashtag '{tag}'")
    else:
        logger.warn(
            f"Out of total {data_type} for the hashtag {tag} {total.total}, only {total.unique} are unique. Something is going wrong..."
        )
