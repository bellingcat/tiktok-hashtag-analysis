# TikTok hashtag analysis toolset 

The tool helps to download posts and videos from TikTok for a given set of hashtags over a period of time. Users can create a growing database of posts for specific hashtags which can then be used for further hashtag analysis. It uses the [TikTokApi](https://github.com/davidteather/TikTok-Api) Python package  to download the posts and uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download the videos.

[![PyPI version](https://badge.fury.io/py/tiktok-hashtag-analysis.svg)](https://badge.fury.io/py/tiktok-hashtag-analysis)

## Pre-requisites
1. Make sure you have Python 3.9 or a later version installed
2. Install the tool with pip: `pip install tiktok-hashtag-analysis`
   - Alternatively you can install directly from the latest version on GitHub: `pip install git+https://github.com/bellingcat/tiktok-hashtag-analysis`
3. Make sure [Playwright](https://playwright.dev/python/docs/intro) is properly installed by running the command `python -m playwright install`

You should now be ready to start using it.

## About the tool
### Command-line arguments
```
usage: tiktok-hashtag-analysis [-h] [--file FILE] [-d] [--number NUMBER] [-p] [-t] [--output-dir OUTPUT_DIR] [--config CONFIG] [--log LOG] [--limit LIMIT] [-v] [--headed] [hashtags ...]

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
  --config CONFIG       File name of configuration file to store TikTok credentials to
  --log LOG             File to write logs to
  --limit LIMIT         Maximum number of videos to download for each hashtag
  -v, --verbose         Increase output verbosity
  --headed              Don't use headless version of TikTok scraper
```

### Structure of output data
```
$ tree ../data
../data
├── london
│   ├── plots
│   ├── posts.json
│   └── media
├── newyork
│   ├── plots
│   ├── posts.json
│   └── media
└── paris
│   ├── plots
│   ├── posts.json
│   └── media
```


The `data` folder contains all the downloaded data as shown in the tree diagram above. 
- Each hashtag has a folder with two subfolders `plots` and `media` that store plots of the most common co-occurring hashtags, and media downloaded from the posts. The posts are stored in the `posts.json` file, and downloaded media is stored as `.mp4` files (for videos) or audio and image files (for image galleries) in the `media` folder.


## How to use
### Post downloading
Running the `tiktok-hashtag-analysis` command with the following options will scrape posts that contain the hashtags `#london`, `#paris`, or `#newyork`:

    tiktok-hashtag-analysis london paris newyork

and will produce an output similar to the following log:

    $ tiktok-hashtag-analysis download london paris newyork
    Hashtags to scrape: ['london', 'paris', 'newyork']
    Scraped 963 posts containing the hashtag 'london'
    Scraped 961 posts containing the hashtag 'paris'
    Scraped 940 posts containing the hashtag 'newyork'
    Successfully scraped 2864 total entries

- The list of hashtags to scrape is specified as a positional argument

### Video downloading
Running the `tiktok-hashtag-analysis` script with the following options will scrape trending posts containing the hashtag `#london`:
`tiktok-hashtag-analysis london --download`

- The `--download` flag specifies that video files for scraped posts should be downloaded

Note that video downloading is a time and data rate consuming task, as a result we recommend using one hashtag at a time when using the `--download` flag to avoid complications.

## Analyzing results 
### Most common co-occurring hashtags
In addition to scraping data and downloading media, the `tiktok-hashtag-analysis` script can also analyze the frequencies of the most common co-occurring hashtags in a given set of posts.

Assume we want to analyze the 20 most frequently co-occurring hashtags in the downloaded posts of the `#london` hashtag.

- The results can be plotted and saved as a PNG file by executing the following command: 

    `tiktok-hashtag-analysis london --number 20 --plot`
    
    which will produce a figure similar to that shown below:
    <p align="center">
        <img src="https://user-images.githubusercontent.com/18430739/166878928-d146b352-b68c-4ab4-bd2c-feb2f0140df9.png" height="500" alt="Top 20 most frequent common hashtags in posts containing the #london hashtag">
    </p>
    
    In the above plot, the highest occurrence is the `#fyp` hashtag, which is tagged in more than half of all posts containing the `#london` hashtag.

- The results can be displayed in tabular form by executing the following command:

    `tiktok-hashtag-analysis london --number 20 --table`

    which will produce a terminal output similar to the following:
    ```
    Co-occurring hashtags for #london posts
    Rank     Hashtag                        Occurrences     Frequency      
    0        london                         881             1.0000
    1        fyp                            399             0.4529
    2        uk                             174             0.1975
    3        foryou                         168             0.1907
    4        viral                          152             0.1725
    5        foryoupage                     137             0.1555
    6        fypシ                           73              0.0829
    7        funny                          54              0.0613
    8        tiktok                         43              0.0488
    9        trending                       43              0.0488
    10       british                        41              0.0465
    11       england                        38              0.0431
    12       xyzbca                         34              0.0386
    13       fy                             33              0.0375
    14       usa                            33              0.0375
    15       love                           29              0.0329
    16       comedy                         25              0.0284
    17       royalfamily                    23              0.0261
    18       queen                          23              0.0261
    19       queenelizabeth                 22              0.0250
    Total posts: 881
    ```

    The `Frequency` column shows the ratio of the occurrence to the total number of downloaded posts.

### Contributing
To run the build-in tests in the `tests/` directory, first install the test dependency packages:

```
pip install .[dev]
```

and then run the tests using the following command:

```
pytest
```

This repo uses [black](https://github.com/psf/black) to format source code and [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking. Before submitting a pull request, please run both tools on the source code.
