import os
import json
from pathlib import Path
from collections import Counter
from datetime import datetime
import warnings
import asyncio
import logging
import re
from urllib.error import HTTPError
from typing import List, Dict, Optional

import yt_dlp
from yt_dlp.utils import ExtractorError, DownloadError
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    TryAgain,
    wait_exponential,
)
from playwright._impl._api_types import Error
from TikTokApi import TikTokApi


warnings.filterwarnings("ignore", message="Glyph (.*) missing from current font")
sns.set_theme(style="darkgrid")

logger = logging.getLogger(__name__)


def process_hashtag_list(hashtags: List[str]) -> List[str]:
    """Convert a list of hashtags to a standard form (remove whitespace, make
    lowercase, etc.)."""
    return list(
        filter(None, (hashtag.strip().strip("#").lower() for hashtag in hashtags))
    )


def load_hashtags_from_file(file: str) -> List[str]:
    """Read and process hashtags specified in a text file."""
    if not os.path.isfile(file):
        raise OSError(f"{file} does not exist")
    with open(file, "r", encoding="utf-8") as f:
        hashtags = re.split(r"\n|,", f.read())
    return process_hashtag_list(hashtags=hashtags)


# Retry upon encountering transient playwright errors
@retry(retry=retry_if_exception_type(Error), stop=stop_after_attempt(3))
async def _fetch_hashtag_data(
    hashtag: str, limit: int, headed: bool = False
) -> List[Dict]:
    """Fetch data for videos containing a specified hashtag, asynchronously."""
    data = []
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[], num_sessions=1, sleep_after=3, headless=not headed
        )
        async for video in api.hashtag(name=hashtag).videos(count=limit):
            data.append(video.as_dict)
    return data


def json_load(file_path: Path) -> List:
    """Read a JSON file and return the read data."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(fp=f)
    return data


def json_dump(file_path: Path, data: List):
    """Write data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(obj=data, fp=f)


@retry(wait=wait_exponential(multiplier=1, max=10))
def _get(url: str) -> requests.Response:
    """Safe version of requests.get that can handle timeouts and retries"""

    r = requests.get(url=url, timeout=30)
    if r.status_code not in {200, 403}:
        raise TryAgain
    else:
        return r


def download_file_and_save(url: str, filepath: Path):
    """Download a file from a specified URL and write its contents to a file"""

    r = _get(url=url)
    if r.status_code == 403:
        return
    ext = r.headers["Content-Type"].split("/")[-1]
    path_with_ext = filepath.with_suffix(f".{ext}")
    with open(path_with_ext, "wb") as f:
        f.write(r.content)
        logger.debug(f"Saved file to: {path_with_ext}")


def download_gallery(video_data: Dict, video_dir: Path):
    """yt-dlp doesn't support downloading images from an image gallery,
    so this downloads all images and audio files from image galleries."""

    video_id = video_data["id"]
    # A small percentage of image galleries don't have an associated audio file
    if play_url := video_data["music"]["playUrl"]:
        filepath = video_dir / f"{video_id}"
        download_file_and_save(url=play_url, filepath=filepath)

    for i, image in enumerate(video_data["imagePost"]["images"]):
        image_url = image["imageURL"]["urlList"][0]
        filepath = video_dir / f"{video_id}_{i:02d}"
        download_file_and_save(url=image_url, filepath=filepath)


def aggregate_cooccurring_hashtags(hashtag_file: Path) -> Counter:
    """Aggregate how frequently hashtags are used, from a file containing a
    list of raw TikTok post API responses."""
    videos = json_load(file_path=hashtag_file)

    all_hashtags: List[set] = []
    for video in videos:
        video_hashtags = set(
            hashtag["hashtagName"]
            for hashtag in video.get("textExtra", [])
            if hashtag.get("hashtagName")
        )
        all_hashtags.extend(video_hashtags)

    return Counter(all_hashtags)


class TikTokDownloader:
    """Main class for scraping data from TikTok."""

    def __init__(
        self, hashtags: List[str], data_dir: Path, config_file: Optional[str] = None
    ):
        self.hashtags = process_hashtag_list(hashtags)

        self.data_dir = Path(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

        self.prioritize_hashtags()
        logger.info(f"Hashtags to scrape: {self.hashtags}")
        logger.info(f"Writing data to directory: {self.data_dir}")

    def prioritize_hashtags(self):
        """Order hashtags based on whether they've been scraped before, and
        the time they were most recently scraped"""

        last_edited = {
            file.parts[-2]: file.lstat().st_mtime
            for file in self.data_dir.glob("*/posts.json")
        }
        self.hashtags.sort(key=lambda h: last_edited.get(h, 0))

    def get_hashtag_posts(self, hashtag: str, limit: int, headed: bool):
        """Fetch data about posts that used a specified hashtag and merge with
        existing data, if it exists."""

        # Define file to store hashtags in and create parent directory
        hashtag_file = self.data_dir / hashtag / "posts.json"
        hashtag_file.parent.mkdir(exist_ok=True, parents=True)

        # If there are previously scraped posts, load them
        if hashtag_file.is_file():
            already_fetched_data = json_load(file_path=hashtag_file)
        else:
            already_fetched_data = []
        already_fetched_ids = set(video["id"] for video in already_fetched_data)

        # Scrape posts that use the specified hashag
        # Attempt to be robust against TikTok's countermeasures for headless browsing
        try:
            fetched_data = asyncio.run(
                _fetch_hashtag_data(hashtag=hashtag, limit=limit, headed=headed)
            )
        except Exception as e:
            logger.warning(
                f"Encountered error {e} when fetching data, retrying in headed mode"
            )
            fetched_data = asyncio.run(
                _fetch_hashtag_data(hashtag=hashtag, limit=limit, headed=True)
            )

        fetched_ids = set(video["id"] for video in fetched_data)

        if len(fetched_data) == 0:
            logger.warning(f"No posts were found for the hashtag: {hashtag}")

        # Determine which newly scraped posts haven't been scraped before
        old_fetched_data = [
            video for video in already_fetched_data if video["id"] not in fetched_ids
        ]
        new_post_count = len(fetched_ids - already_fetched_ids)
        old_post_count = len(already_fetched_ids)

        # Merge new and old data and write to file
        all_fetched_data = old_fetched_data + fetched_data
        json_dump(file_path=hashtag_file, data=all_fetched_data)
        logger.info(
            f"Scraped {new_post_count} new posts containing the hashtag "
            f"'{hashtag}', with {old_post_count} posts previously scraped"
        )

    def get_hashtag_videos(self, hashtag: str):
        """Download videos and other media corresponding to posts that used a
        specified hashtag,"""

        # Define file containing post data and directory to save videos to
        hashtag_file = self.data_dir / hashtag / "posts.json"
        video_dir = self.data_dir / hashtag / "media"
        video_dir.mkdir(exist_ok=True)

        # Get list of post IDs that have previously had their media downloaded
        already_downloaded_ids = set(
            file.split(".")[0].split("_")[0] for file in os.listdir(video_dir)
        )
        # Get list of posts that have been scraped but not had their media downloaded
        video_list = json_load(file_path=hashtag_file)
        new_video_list = [
            video for video in video_list if video["id"] not in already_downloaded_ids
        ]

        # Populate list of URLs to download using yt-dlp, and list of image
        # galleries to download using the `download_gallery` function
        urls_to_download = []
        galleries_to_download = []
        for video in new_video_list:
            if video.get("imagePost") is None:
                if video.get("author") is None:
                    continue
                url = f"https://www.tiktok.com/@{video['author']['uniqueId']}/video/{video['id']}"
                urls_to_download.append(url)
            else:
                galleries_to_download.append(video)

        # Download audio and image files for all image gallery posts
        if len(galleries_to_download) > 0:
            logger.info(f"Downloading image galleries for hashtag {hashtag}")
        for video in galleries_to_download:
            logger.debug(f"Downloading image gallery for video: {video['id']}")
            download_gallery(video_data=video, video_dir=video_dir)

        # Download video files for all video posts
        if len(urls_to_download) > 0:
            logger.info(f"Downloading media for hashtag {hashtag}")

        ydl_opts = {
            "outtmpl": os.path.join(video_dir, "%(id)s.%(ext)s"),
            "ignore_errors": True,
            "quiet": logger.getEffectiveLevel() > logging.DEBUG,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls_to_download:
                try:
                    ydl.download([url])
                except (HTTPError, TypeError, ExtractorError, DownloadError) as e:
                    # Catch urllib and yt-dlp errors when video not found
                    logger.warning(
                        f"Encountered error {e} when attempting to download url: {url}"
                    )

    def frequency_table(self, hashtag: str, number: int):
        """Print `number`-most commonly co-occurring hashtags for a specified
        source hashtag, in tabular form."""

        # Load video data file and extract co-occurring hashtag frequency information
        hashtag_file = self.data_dir / hashtag / "posts.json"
        frequencies = aggregate_cooccurring_hashtags(hashtag_file=hashtag_file)

        # Print table that displays most commonly co-occurring hashtags
        total_posts = max(frequencies.values())
        print(f"\nCo-occurring hashtags for #{hashtag} posts")
        print(f"{'Rank':<8} {'Hashtag':<30} {'Occurrences':<15} {'Frequency':<15}")
        for row, (hashtag, frequency) in enumerate(frequencies.most_common(number)):
            ratio = frequency / total_posts
            print(f"{row:<8} {hashtag:<30} {frequency:<15} {ratio:.4f}")
        print(f"Total posts: {total_posts}\n\n")

    def plot(self, hashtag: str, number: int):
        """Create plot of `number`-most commonly co-occurring hashtags for a
        specified source hashtag."""

        # Load video data file and extract co-occurring hashtag frequency information
        hashtag_file = self.data_dir / hashtag / "posts.json"
        frequencies = aggregate_cooccurring_hashtags(hashtag_file=hashtag_file)

        # Define labels and other fields used in plot
        total_posts = max(frequencies.values())
        frequencies.pop(hashtag)
        sorted_frequencices = frequencies.most_common(number)
        labels = [label for label, _ in sorted_frequencices]
        ratios = [freq / total_posts * 100 for _, freq in sorted_frequencices]
        y_pos = list(reversed(range(len(sorted_frequencices))))

        # Visualize data in bar chart
        fig, ax = plt.subplots(figsize=(5, 6.66))
        ax.barh(y_pos, ratios)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.grid(axis="y")
        ax.set_xlabel("Percent of posts with co-occurring hashtag")
        ax.set_ylim(min(y_pos) - 1, max(y_pos) + 1)
        ax.set_title(f"Co-occurring hashtags for #{hashtag} posts")
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

        # Write image of plot to file
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        plot_file = self.data_dir / hashtag / "plots" / f"{hashtag}__{current_time}.png"
        plot_file.parent.mkdir(exist_ok=True, parents=True)
        plt.savefig(plot_file, bbox_inches="tight", facecolor="white", dpi=300)
        logger.info(f"Plot saved to file: {plot_file}")

    def run(
        self,
        limit: int,
        download: bool,
        plot: bool,
        table: bool,
        number: int,
        headed: bool,
    ):
        """Execute the specified operations on all specified hashtags."""

        # Scrape all specified hashtags and perform analyses, depending on if
        # `--table`, `--plot`, and `--download` flags are used in the command
        for hashtag in self.hashtags:
            self.get_hashtag_posts(hashtag=hashtag, limit=limit, headed=headed)
            if plot:
                self.plot(hashtag=hashtag, number=number)
            if table:
                self.frequency_table(hashtag=hashtag, number=number)
            if download:
                self.get_hashtag_videos(hashtag=hashtag)
