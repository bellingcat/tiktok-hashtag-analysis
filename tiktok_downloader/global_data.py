# Directories
DATA = "../data"
IDS = "ids"
LOG = "log"
POSTS = "posts"
VIDEOS = "videos"
IMAGES = f"{DATA}/img"

# Files
POST_IDS = "post_ids.json"
VIDEO_IDS = "video_ids.json"
DATA_FILE = "data.json"
LOG_FILE = "log.json"


FILES = {
            "data" : DATA,
            "ids" : IDS,
            "log" : LOG,
            "posts" : POSTS,
            "videos" : VIDEOS,
            "images" : IMAGES,
            "post_ids" : f"{DATA}/{IDS}/{POST_IDS}",
            "video_ids" : f"{DATA}/{IDS}/{VIDEO_IDS}",
            "data_file" : f"{DATA_FILE}",
            "downloads" : [],
            "logger" : f"{DATA}/{LOG}/{LOG_FILE}",
        }



# Commands
tag = ""

PARAMETERS = {
            "scraper_attempts" : 3,
#            "number_of_videos" : 3, # Number of videos to be downloaded by tiktok-scraper.
}
COMMANDS = {
    "number_of_videos" : 3, # Number of videos to be downloaded by tiktok-scraper.
    "post_download" : f"tiktok-scraper hashtag {tag} -t 'json'",
    "video_download" : f"tiktok-scraper hashtag {tag} -d",
    "sleep" : 8
        }
