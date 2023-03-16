# TikTok hashtag analysis toolset 

> IMPORTANT NOTE: this tool relies on [drawrowfly/tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper) which seems to be broken at time of writing and without updates for some time with several open issues ([796](https://github.com/drawrowfly/tiktok-scraper/issues/796) [#799](https://github.com/drawrowfly/tiktok-scraper/issues/799)) that need to be fixed before this library can work smoothly :/

The tool helps to download posts and videos from TikTok for a given set of hashtags over a period of time. Users can create a growing database of posts for specific hashtags which can then be used for further hashtag analysis. It uses the [tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper) Node package  to download the posts and videos.

[![PyPI version](https://badge.fury.io/py/tiktok-hashtag-analysis.svg)](https://badge.fury.io/py/tiktok-hashtag-analysis)

## Pre-requisites
1. Make sure you have Python 3.6 or a later version installed
2. And, you need to have node version 16. On Mac, do `brew install node` followed by `npm install -g n` and then `n 16`
4. Download and install TikTok scraper: https://github.com/drawrowfly/tiktok-scraper 
5. Install the tool with pip: `pip install tiktok-hashtag-analysis`
   1. or directly from the repo version: `pip install git+https://github.com/bellingcat/tiktok-hashtag-analysis`

You should now be ready to start using it.


## About the tool
### Command-line arguments
```
tiktok-hashtag-analysis --help
usage: tiktok-hashtag-analysis [-h] [-t [T ...]] [-f F] [-p] [-v] [-ht HASHTAG] [-n NUMBER] [-plt] [-d] {download,frequencies}

Analyze hashtags within posts scraped from TikTok.

positional arguments:
  {download,frequencies}
                        command to initialize

options:
  -h, --help            show this help message and exit
  -t [T ...]            List of hashtags to scrape (module: run_downloader)
  -f F                  File name containing list of hashtags to scrape (module: run_downloader)
  -p                    Download post data (module: run_downloader)
  -v                    Download video files (module: run_downloader)
  -ht HASHTAG, --hashtag HASHTAG
                        The hashtag of scraped posts to analyze (module: hashtag_frequencies)
  -n NUMBER, --number NUMBER
                        The number of top n occurrences (module: hashtag_frequencies)
  -plt, --plot          Plot the occurrences (module: hashtag_frequencies)
  -d, --print           List top n hashtags (module: hashtag_frequencies)
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
Running the `tiktok-hashtag-analysis download` command with the following options will scrape posts containing the hashtags `#london`, `#paris`, or `#newyork`:

    tiktok-hashtag-analysis download -t london paris newyork -p

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

    `tiktok-hashtag-analysis frequencies london 20 -p`
    
    which will produce a figure similar to that shown below:
    <p align="center">
        <img src="https://user-images.githubusercontent.com/18430739/166878928-d146b352-b68c-4ab4-bd2c-feb2f0140df9.png" height="500" alt="Top 20 most frequent common hashtags in posts containing the #london hashtag">
    </p>
    
    In the above plot, the highest occurrence is the `#fyp` hashtag, which is tagged in more than half of all posts containing the `#london` hashtag.

- The results can be displayed in tabular form by executing the following command:

    `tiktok-hashtag-analysis frequencies london 20 -d`

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
