from utils.utils import get_filepath_from_link
import urllib.request
import urllib.error
from os.path import join, isfile
from os import makedirs
from tqdm import tqdm
from random import randrange
import collections
import time


def get_links_dict(segments_filepath):
    '''
    Get the links from segments filepath
    '''
    with open(segments_filepath) as f :
        content_data = f.readlines()

    links_dict = {}
    for i, line in enumerate(tqdm(content_data)):
        filename, link, _, _ = line.strip().split("\t")
        # Get output folder to download file from link
        speakerid, bookid, fileid = filename.split('_')
        output_folder = join(speakerid, bookid)
        # Change link 64 to 128
        #link = get_better_quality_link(link)
        # Insert link => output folder at links_dict
        if not link in links_dict.keys():
            links_dict[link] = output_folder

    # Sorting dict by key (link)
    ordered_links_dict = collections.OrderedDict(sorted(links_dict.items()))
    return ordered_links_dict


def download_mp3_from_dict(links_dict, output_dir):
    '''
    Given a list of links, downloads mp3 files at 64kbs.
    '''
    for i, (link, folder) in enumerate(tqdm(links_dict.items())):
        # Getting complete filepath
        output_path = join(output_dir, folder)
        makedirs(output_path, exist_ok=True)
        mp3_filepath = get_filepath_from_link(link, output_path)
        # Print status
        #print('Download {} / {} file: {}'.format(i, total, mp3_filename))
        # Verify if mp3 file exists]
        if not isfile(mp3_filepath):
            # if site is down wait
            while True:
                try:
                    if urllib.request.urlopen("http://archive.org/").getcode() == 200:
                        break
                except:
                    time.sleep(10)
            try:
                urllib.request.urlretrieve(link, mp3_filepath)
            except:
                print("Conection problem to acess {}... ".format(link))
                continue

        # Wait to avoid ip blocking
        time.sleep(randrange(15,30))
    return True