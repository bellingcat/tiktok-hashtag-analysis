# TikTok hashtag analysis toolset 
The tool helps to download posts and videos from tiktok for a given set of hashtags. It uses tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper) to download the posts and videos.

## Pre-requisites
1. Make sure you have python 3.6 or later version installed.
2. Download and install TikTok scraper: https://github.com/drawrowfly/tiktok-scraper 

### Options for running run_downloader.py

<code> python3 run_downloader.py -h </code>


<img width="686" alt="Screenshot 2022-02-25 at 19 04 26" src="https://user-images.githubusercontent.com/72805812/155765360-47f0956c-220a-4098-8d52-1304a9f11e69.png">



### Data organization

<code> tree ../data </code>

<img width="488" alt="Screenshot 2022-02-25 at 19 21 44" src="https://user-images.githubusercontent.com/72805812/155767522-94bd3774-60eb-45fc-8129-b2abc59c6089.png">

<code>data</code> folder contains all the downloaded data as shown in the pic above. 
1. the <code>log</code> folder contains log.json which records the total number of downloaded posts and videos for the hashtags against the time stamp of when the script is run.
2. the <code>ids</code> folder contains two files <code>post_ids.json</code> and <code>video_ids.json</code> that records the ids of the downloaded posts and videos for each hashtag.
3. Each hashtag has a folder with two subfolders <code>posts</code> and <code>videos</code> that store posts and videos respectively. The posts are stored in the <code>data.json</code> file in the <code>posts</code> folder, and videos are stored as the <code>.mp4</code> files in the <code>videos</code> folder.



### Post download 
Run the run_downloader.py with the following option:
         <code> python3 run_downloader.py --h london paris newyork -p </code>

<img width="1301" alt="Screenshot 2022-02-25 at 19 14 06" src="https://user-images.githubusercontent.com/72805812/155766542-7de77313-6389-4ea2-aca5-b5f39fd70160.png">

1. The --h option allows to type in hashtag list in the commandline.
2. -p option specifies the download posts option.


### Video download 
<code> python3 run_downloader.py --h london -v</code>

1. --h option allows to type in the list of hashtags as command line argument.
2. -v option is for downloading the videos
The above code download all the trending videos for the hashtag london. Note that video downloading is a time and data rate consuming task, as a result we strongly recommend to use one hashtag at a time so as to avoid complications.


### Top n hashtag occurrences 
In the analytics folder, the file <code>hashtag_frequencies.py</code> will plot the frequencies of top occurring hashtags in a given set of posts.
Assume we want to plot the graph of top 20 occurring hashtags in the downloaded posts of the hashtag london.

1. Plotting the saving the image as a png file: <code> python3 hashtag_frequencies.py -p ../data/london/posts/data.json 20 -v</code>

<img width="1390" alt="Screenshot 2022-02-25 at 19 45 40" src="https://user-images.githubusercontent.com/72805812/155770710-0d167bbb-4c44-44d2-ba1c-fa57026afea8.png">

The figure above shows the top 20 occurring hashtags among all the posts downloaded for the hashtag london. Clearly, the highest occurrence will be of the hashtag london as the file <code>data/london/posts/data.json</code> contain all the posts with hashtag london.

2. Printing the result in the shell: <code> python3 hashtag_frequencies.py -d ../data/london/posts/data.json 20 -v</code>
<img width="807" alt="Screenshot 2022-02-25 at 19 54 09" src="https://user-images.githubusercontent.com/72805812/155771757-e71b2858-cd9c-4496-8cc5-76146e8a8d32.png">

The same result of 1 is printed in the shell. The last column shows the ratio of the occurrence to the total posts.


