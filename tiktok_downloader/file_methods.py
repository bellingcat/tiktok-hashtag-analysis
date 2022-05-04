import os, json, subprocess
from datetime import datetime
import global_data
import shutil


# setting up the logging
import logging
from logging.config import fileConfig

fileConfig('../logging.ini')
logger = logging.getLogger()



"""
The file contains the functions that operate on files, such as writing or reading from files etc.
"""


def create_file(name, file_type):
    """
    Creates a file or directory.
    """
    if (file_type == "dir"):
        os.makedirs(name, mode=0o777)
    elif (file_type == "file"):
        with open(name, "w"): pass
    else:
        logger.exception(f"{file_type} has to be a 'dir' or a 'file'!!!")
    return


def check_existence(file_path, file_type):
    """
    Checks the existence of a file or a directory. If not found, returns False, else returns True.
    """
    if (file_type == "file"):
        return os.path.isfile(file_path)
    elif (file_type == "dir"):
        return os.path.isdir(file_path)
    else:
        logger.exception(f"{file_type} has to be a 'dir' or a 'file'!!!")


def check_file(file_path, file_type):
    """
    Creates a file or directory, if not found. Else, returns nothing.
    """
    status = check_existence(file_path, file_type)
    if not status:
        create_file(file_path, file_type)    

    return


def download_posts(settings, tag):
    """
    Runs the tiktok-scraper command to download posts for a given hashtag.
    Returns the path to the downloaded file of posts. If no file was downloaded, prints the error and returns nothing in order to move on.
    os.chdir is used to execute shell commands in the right folders and then reused to come back to the original folder of execution of run_downloader script.
    """
    path = os.path.join(settings["data"], tag, settings["posts"])
    os.chdir(path)
    try:
        tiktok_command = f"tiktok-scraper hashtag {tag} -t 'json'" 
        result = subprocess.check_output(tiktok_command, shell=True)
        print(result)
        new_file = result.decode('utf-8').split()[-1]
        if ("json" in new_file):
            os.chdir("../../../tiktok_downloader")
            return new_file 
        else:
            logger.warn(f"WARNING: Something's wrong with what is returned by tiktok-scraper for the hashtag {tag} - *{new_file}* is not a json file!!!!")
            os.chdir("../../../tiktok_downloader")
            return
    except: raise



def download_videos(settings, tag):
    """
    Runs the tiktok-scraper command to download videos for a given hashtag. Note that all the videos are downloaded that are returned by the tiktok api and as a result, its a time and data consuming process. 
    The list of downloaded video ids is constucted and returned if the downloaded folder contains at least 1 video.
    os.chdir is used to execute shell commands in the right folders and then reused to come back to the original folder of execution of run_downloader script.
    """
    path = os.path.join(settings["data"], tag, settings["videos"])
    os.chdir(path)
    try:
        # tiktok_command = f"tiktok-scraper hashtag {tag} -n {settings['number_of_videos']} -d" 
        tiktok_command = f"tiktok-scraper hashtag {tag} -d" 
        result = subprocess.check_output(tiktok_command, shell=True)
        downloaded_list_tmp = os.listdir(f"./#{tag}")
        if downloaded_list_tmp:
            downloaded_list = []
            for file in downloaded_list_tmp:
                file = file.split('.')[0]
                downloaded_list.append(file)
            
            os.chdir("../../../tiktok_downloader")
            return downloaded_list
        else:
            print(f"WARNING: No video files were downloaded for the hashtag {tag}.")
            os.chdir("../../../tiktok_downloader")
            shutil.rmtree(settings['videos_delete'])
            #subprocess.call(f"rm -rf {settings['videos_delete']}", shell=True)
        
    except: raise


def get_data(file_path):
    """
    Reads the json file and retuns the read data.
    """
    with open(file_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
        return data


def dump_data(file_path, data):
    """
    Writes the data to the json file.
    """
    with open(file_path, "w", encoding = "utf-8") as f:
        json.dump(data, f)
        return            

def log_writer(log_data):
    """
    Creates the dictionary of total downloads (posts and videos) per hashtag.
    Example : {timstamp : {hashtag : { videos : number_of_new_videos , posts : number_of_new_posts } } }
    Writes the dictionary to the log file (logs/log.json).
    """
    total = 0
    try:
        log_dict = {}
        for ele in log_data:
            if ele[0] in log_dict:
                if ele[1][0] in log_dict[ele[0]]:
                    log_dict[ele[0]][ele[1][0]] += ele[1][1]
                else:
                    log_dict[ele[0]][ele[1][0]] = ele[1][1]
                total += ele[1][1]
            else:
                log_dict[ele[0]] = { ele[1][0] : ele[1][1] }
                total += ele[1][1]

        now = datetime.now()
        now_str = now.strftime("%d-%m-%Y %H:%M:%S")
        data = { now_str : log_dict }

        logger.warn(data)
        logger.info(f"Successfully logged {total} entries!!!!")
        return
    except:
        logger.exception()


def id_writer(file_path, new_data, tag, status):
    """
    Writes the list of new ids to the post_ids or video_ds files.
    """
    try:
        total = len(new_data)
        if status:
            try:
                data = get_data(file_path)
                if tag in data:
                    data[tag] += new_data
                else:
                    data[tag]= new_data 
                dump_data(file_path, data)
            except json.decoder.JSONDecodeError:
                data = { tag : new_data }
                dump_data(file_path, data)
        else:
            data = { tag : new_data }
            dump_data(file_path, data)
        logger.info(f"SUCCESS - {total} entries added to {file_path}!!!")
        log_data = (tag, total)
        return log_data
    except:
        logger.exception()


def post_writer(file_path, new_data, status):
    """
    Writes the new posts in the post file of the given hashtag (/data/{hashtag}/posts/data.json)
    """
    try:
        total = len(new_data)
        if status:
            try:
                data = get_data(file_path)
                data += new_data
                dump_data(file_path, data)
            except json.decoder.JSONDecodeError:
                data = new_data
                dump_data(file_path, data)
        else:
            data = new_data
            dump_data(file_path, data)
        logger.info(f"SUCCESS - {total} entries added to {file_path}!!!")
        return
    except:
        logger.exception()


def delete_file(file_path, file_type):
    """
    Deletes the directory or the file.
    """
    if not check_existence(file_path, file_type):
        logger.exception(f"ERROR: Attempt to delete failed. {file_path} does not exist!!!")
    elif (file_type == "file"):
        os.remove(file_path)
        logger.info(f"Successfully deleted {file_path}!!!")
        return
    elif (file_type == "dir"):
        os.rmdir(file_path)
        logger.info(f"Successfully deleted {file_path}!!!")
        return
    else:
        logger.exception(f"OSError: {file_type} needs to be either 'file' or 'dir' !!!")


def clean_video_files(settings, tag, new_data=None):
    """
    Moves the new videos from the tiktok-scraper video folder to /data/{hashtag}/videos/
    Deletes the residual tiktok-scraper video folder.
    """
    try:
        if new_data:
            for file in new_data:
                settings["videos_from"] = settings['data'] + f"/{tag}/videos/#{tag}/{file}.mp4"
                shutil.move(settings['videos_from'], settings['videos_to'])
             
        shutil.rmtree(settings['videos_delete'])
        logger.info(f"Successfully deleted the folder {settings['videos_delete']} folder of videos.")
    except:
        raise
