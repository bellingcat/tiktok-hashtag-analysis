# TikTok hashtag analysis toolset 

The tool helps to download posts and videos from TikTok for a given set of hashtags over a period of time. Users can create a growing database of posts for specific hashtags which can then be used for further hashtag analysis. It uses the [TikTokApi](https://github.com/davidteather/TikTok-Api) Python package  to download the posts and uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download the videos.

[![PyPI version](https://badge.fury.io/py/tiktok-hashtag-analysis.svg)](https://badge.fury.io/py/tiktok-hashtag-analysis)

## Pre-requisites
1. Make sure you have Python 3.9 or a later version installed
2. Install the tool with pip: `pip install tiktok-hashtag-analysis`
   1. or directly from the repo version: `pip install git+https://github.com/bellingcat/tiktok-hashtag-analysis`

You should now be ready to start using it.


## About the tool
### Command-line arguments
```
usage: tiktok-hashtag-analysis [-h] [--file FILE] [-d] [--number NUMBER] [-p] [-t] [--output-dir OUTPUT_DIR] [--log LOG] [hashtags ...]

Analyze hashtags within posts scraped from TikTok.

positional arguments:
  hashtags              List of hashtags to scrape

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           File name containing list of hashtags to scrape
  -d, --download        Download video files corresponding to scraped posts
  --number NUMBER       The number of co-occurring hashtags to analyze
  -p, --plot            Plot the most common co-occurring hashtags
  -t, --table           Print a table of the most common co-occurring hashtags
  --output-dir OUTPUT_DIR
                        Directory to save scraped data and visualizations to
  --log LOG             File to write logs to
```

### Structure of output data
```
$ tree ../data
../data
├── ids
│   └── post_ids.json
├── london
│   └── posts
│       └── data.json
├── newyork
│   └── posts
│       └── data.json
└── paris
    └── posts
        └── data.json
```


The `data` folder contains all the downloaded data as shown in the tree diagram above. 
- The `ids` folder contains two files `post_ids.json` and `video_ids.json` that record the ids of the downloaded posts and videos for each hashtag.
- Each hashtag has a folder with two subfolders `posts` and `videos` that store posts and videos respectively. The posts are stored in the `data.json` file in the `posts` folder, and videos are stored as the `.mp4` files in the `videos` folder.


## How to use
### Post downloading
Running the `tiktok-hashtag-analysis` command with the following options will scrape posts containing the hashtags `#london`, `#paris`, or `#newyork`:

    tiktok-hashtag-analysis london paris newyork

and will produce an output similar to the following log:

    $ tiktok-hashtag-analysis download -t london paris newyork -p
    Hashtags to scrape: ['london', 'paris', 'newyork']
    Scraped 963 posts containing the hashtag 'london'
    Scraped 961 posts containing the hashtag 'paris'
    Scraped 940 posts containing the hashtag 'newyork'
    Successfully scraped 2864 total entries

- The `-t` flag allows a space-separated list of hashtags to be specified as a command line argument
- The `-p` flag specifies that posts, not videos, will be downloaded

### Video downloading
Running the `tiktok-hashtag-analysis download` script with the following options will scrape trending videos containing the hashtag `#london`:
`tiktok-hashtag-analysis download -t london -v`

- The `-t` flag allows a space-separated list of hashtags to be specified as a command line argument
- The `-v` flag specifies that videos, not posts, will be downloaded

Note that video downloading is a time and data rate consuming task, as a result we recommend using one hashtag at a time when using the `-v` flag to avoid complications.

## Analyzing results 
### Top n hashtag occurrences 
The script `tiktok-hashtag-analysis frequencies` analyzes the frequencies of top occurring hashtags in a given set of posts.

Assume we want to analyze the 20 most frequently occurring hashtags in the downloaded posts of the `#london` hashtag.

- The results can be plotted and saved as a PNG file by executing the following command: 

    `tiktok-hashtag-analysis frequencies --hashtag london --number 20 --plot`
    
    which will produce a figure similar to that shown below:
    <p align="center">
        <img src="https://user-images.githubusercontent.com/18430739/166878928-d146b352-b68c-4ab4-bd2c-feb2f0140df9.png" height="500" alt="Top 20 most frequent common hashtags in posts containing the #london hashtag">
    </p>
    
    In the above plot, the highest occurrence is the `#fyp` hashtag, which is tagged in more than half of all posts containing the `#london` hashtag.

- The results can be displayed in tabular form by executing the following command:

    `tiktok-hashtag-analysis frequencies --hashtag london --number 20 --print`

    which will produce a terminal output similar to the following:
    ```
    Rank     Hashtag                        Occurrences     Frequency
    0        london                         960             1.0000
    1        fyp                            494             0.5146
    2        uk                             238             0.2479
    3        foryou                         221             0.2302
    4        foryoupage                     184             0.1917
    5        viral                          179             0.1865
    6        fypシ                           84              0.0875
    7        funny                          56              0.0583
    8        xyzbca                         51              0.0531
    9        british                        45              0.0469
    10       england                        44              0.0458
    11       trending                       40              0.0417
    12       fy                             33              0.0344
    13       comedy                         32              0.0333
    14       roadman                        28              0.0292
    15       4u                             27              0.0281
    16       usa                            26              0.0271
    17       tiktok                         26              0.0271
    18       travel                         21              0.0219
    19       america                        20              0.0208
    Total posts: 960
    ```

    The `Frequency` column shows the ratio of the occurrence to the total number of downloaded posts.
