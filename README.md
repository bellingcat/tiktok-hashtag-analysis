# tiktok hashtag analysis toolset 
The project provides tools to analyze hashtags based on data downloaded using tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper).

## Pre-conditions
1. Download and install TikTok scraper: https://github.com/drawrowfly/tiktok-scraper

## extract_date.py
1. Use the following command: python3 extract_date.py target_file.json hashtag_name
2. The command above uses the extract_date.py script to extract the dates and the corresponding number of hashtag posts for each date that the TikTok scraper retrieves in the .json file.

## extract_hashtag.py
1. Use the following command: python3 extract_hashtag.py target_file.json n
2. The command above will plot top n hashtag frequencies based on the json file downloaded using tiktok scraper for a given hashtag. Recommendation n < = 10 for easy to read and analyze.

## extract_posts.py
1. Use the following command: python3 extract_posts.py target_file.json hashtag_name
2. The command above pulls out all the posts for the hashtag hashtag_name from the downloaded tiktok scraper data. 
