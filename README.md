# tiktok hashtag analysis toolset 
The project provides tools to analyze hashtags within posts scraped from TikTok.

## extract_date.py
1. Download and install TikTok scraper: https://github.com/drawrowfly/tiktok-scraper
2. Use the following command: python3 extract_date.py target_file.json hashtag


The command in point 2 uses the extract_date.py script to extract the dates and the corresponding number of hashtag posts for each date that the TikTok scraper retrieves in the .json file.

## extract_hashtag.py
1. Use the following command: python3 extract_hashtag.py target_file.json n
2. It will plot top n hashtag frequencies. 

## extract_posts.py
1. Use the following command: python3 extract_posts.py target_file.json hashtag
