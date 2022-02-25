# TikTok hashtag analysis toolset 
The tool helps to download posts and videos from tiktok for a given set of hashtags. It uses tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper) to download the posts and videos.

## Pre-requisites
1. Make sure you have python 3.8 or later version installed.
2. Download and install TikTok scraper: https://github.com/drawrowfly/tiktok-scraper 

### Options for running run_downloader.py

<img width="686" alt="Screenshot 2022-02-25 at 19 04 26" src="https://user-images.githubusercontent.com/72805812/155765360-47f0956c-220a-4098-8d52-1304a9f11e69.png">

### Data organization

<img width="488" alt="Screenshot 2022-02-25 at 19 21 44" src="https://user-images.githubusercontent.com/72805812/155767522-94bd3774-60eb-45fc-8129-b2abc59c6089.png">

<code>data</code> folder contains all the downloaded data as shown in the pic above. 
1. the <code>log</code> folder contains log.json which records the total number of downloaded posts and videos for the hashtags against the time stamp of when the script is run.
2. the <code>ids</code> folder contains two files <code>post_ids.json</code> and <code>video_ids.json</code> that records the ids of the downloaded posts and videos for each hashtag.
3. Each hashtag has a folder with two subfolders <code>posts</code> and <code>videos</code> that store posts and videos respectively. The posts are stored in the <code>data.json</code> file in the <code>posts</code> folder, and videos are stored as the <code>.mp4</code> files in the <code>videos</code> folder.



<img width="1301" alt="Screenshot 2022-02-25 at 19 14 06" src="https://user-images.githubusercontent.com/72805812/155766542-7de77313-6389-4ea2-aca5-b5f39fd70160.png">

### Post download example
Run the run_downloader.py with the following option:
         python3 run_downloader.py --h london paris newyork -p
