import os, json, subprocess
from datetime import datetime
import global_data
import data_methods


def create_file(name, file_type):
    if (file_type == "dir"):
        os.makedirs(name, mode=0o777)
    elif (file_type == "file"):
        with open(name, "w"): pass
    else:
        print(f"ERROR: either {file_type} or is not well defined.")
    return


def check_existence(file_path, file_type):
    if (file_type == "file"):
        if os.path.isfile(file_path):
            return True
        else:
            return False
    elif (file_type == "dir"):
        if os.path.isdir(file_path):
            return True
        else:
            return False
    else:
        raise OSError(f"{file_type} has to be a 'dir' or a 'file'!!!")


def check_file(file_path, file_type):
    status = check_existence(file_path, file_type)
    if not status:
        create_file(file_path, file_type)    

    return


def download_posts(settings, tag):
    path = os.path.join(settings["data"], tag, settings["posts"])
    os.chdir(path)
    try:
        tiktok_command = f"tiktok-scraper hashtag {tag} -t 'json'" 
        result = subprocess.run([tiktok_command], capture_output=True, shell=True)
        if result.stdout:
            new_file = result.stdout.decode('utf-8').split()[-1]
            if ("json" in new_file):
                os.chdir("../../../tiktok_downloader")
                return new_file 
            else:
                print(f"ERROR: Something's wrong with what is returned by tiktok-scraper for the hashtag {tag} - *{new_file}* is not a json file!!!!")
                os.chdir("../../../tiktok_downloader")
                return
        else:
            os.chdir("../../../tiktok_downloader")
            print(f"ERROR: No file was downloaded by the tiktok-scraper for the {tag} !!!!")
            return
    except: raise



def download_videos(settings, tag):
    path = os.path.join(settings["data"], tag, settings["videos"])
    os.chdir(path)
    try:
<<<<<<< HEAD
        # tiktok_command = f"tiktok-scraper hashtag {tag} -n {settings['number_of_videos']} -d" 
        tiktok_command = f"tiktok-scraper hashtag {tag} -d" 
=======
        tiktok_command = f"tiktok-scraper hashtag {tag} -n {settings['number_of_videos']} -d" 
>>>>>>> bfa90676f121dd88e070dc134791a596a104e784
        result = subprocess.run([tiktok_command], capture_output=True, shell=True)
        if result.stdout:
            downloaded_list_tmp = os.listdir(f"./#{tag}")
            if downloaded_list_tmp:
                downloaded_list = []
                for file in downloaded_list_tmp:
                    file = file[0:-4]
                    downloaded_list.append(file)
                
                os.chdir("../../../tiktok_downloader")
                return downloaded_list
            else:
                print(f"WARNING: No video files were downloaded for the hashtag {tag}.")
                os.chdir("../../../tiktok_downloader")
                subprocess.call(f"rm -rf {settings['videos_delete']}", shell=True)
        else:
            os.chdir("../../../tiktok_downloader")
            print(f"WARNING: Something went wrong with the tiktok-scraper video download for the {tag} !!!!")
            return
        
    except: raise


def get_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
        return data


def dump_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)
        return            

def log_writer(log_data):
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

        logger = global_data.FILES["logger"]
        now = datetime.now()
        now_str = now.strftime("%d-%m-%Y %H:%M:%S")
        status = check_existence(logger, "file")
        if status:
            data = get_data(logger)
            data[now_str] = log_dict
            dump_data(logger, data)
        else:
            data = { now_str : log_dict }
            dump_data(logger, data)
        print(f"Successfully logged {total} entries!!!!")
        return
    except: raise


def id_writer(file_path, new_data, tag, status):
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
        print(f"SUCCESS - {total} entries added to {file_path}!!!")
        log_data = (tag, total)
        return log_data
    except: raise


def post_writer(file_path, new_data, status):
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
        print(f"SUCCESS - {total} entries added to {file_path}!!!")
        return
    except: raise


def delete_file(file_path, file_type):
    if not check_existence(file_path, file_type):
        print(f"ERROR: Attempt to delete failed. {file_path} does not exist!!!")
    elif (file_type == "file"):
        os.remove(file_path)
        print(f"Successfully deleted {file_path}!!!")
        return
    elif (file_type == "dir"):
        os.rmdir(file_path)
        print(f"Successfully deleted {file_path}!!!")
        return
    else:
        print(f"ERROR: {file_type} needs to be either 'file' or 'dir' !!!")
        return


def clean_video_files(settings, tag, new_data=None):
    try:
        if new_data:
            for file in new_data:
                settings["videos_from"] = settings['data'] + f"/{tag}/videos/#{tag}/{file}.mp4"
                subprocess.call(f"mv {settings['videos_from']} {settings['videos_to']}", shell=True)
             
        subprocess.call(f"rm -rf {settings['videos_delete']}", shell=True)
        print(f"Successfully deleted the folder {settings['videos_delete']} folder of videos.")
    except:
        raise
