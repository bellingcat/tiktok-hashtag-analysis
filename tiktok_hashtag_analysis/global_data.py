"""Specify global constants including file paths and scraping options.
"""


# Directories
DATA = "../data"
IDS = "ids"
POSTS = "posts"
VIDEOS = "videos"
IMAGES = f"{DATA}/img"

# Files
POST_IDS = "post_ids.json"
VIDEO_IDS = "video_ids.json"
DATA_FILE = "data.json"

FILES = {
    "data": DATA,
    "ids": IDS,
    "posts": POSTS,
    "videos": VIDEOS,
    "images": IMAGES,
    "post_ids": f"{DATA}/{IDS}/{POST_IDS}",
    "video_ids": f"{DATA}/{IDS}/{VIDEO_IDS}",
    "data_file": f"{DATA_FILE}",
    "downloads": [],
}

PARAMETERS = {
    "scraper_attempts": 3,
    "sleep": 8,
}
