import argparse
import time
from os import makedirs
from os.path import join, isfile, dirname
import urllib.request
import urllib.error
from tqdm import tqdm
from audio_converter import create_audio_files_from_segments_list, create_segments_list
from utils.utils import remove_mp3_files, get_filepath_from_link, get_better_quality_link
from utils.download_dataset import download_language_dataset, extract_segment_files
import collections
from random import randrange

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
        link = get_better_quality_link(link)
        # Insert link => output folder at links_dict
        if not link in links_dict.keys():
            links_dict[link] = output_folder

    # Sorting dict by key (link)
    ordered_links_dict = collections.OrderedDict(sorted(links_dict.items()))
    return ordered_links_dict

def download_mp3_files(links_dict, output_dir):
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

def execute(language, sampling_rate = 22050, audio_format = 'wav', delete_files = False):
    '''
    Execute convertion pipeline.
    '''
    print('Downloading {} dataset tar.gz file...'.format(language))
    tar_filename = download_language_dataset(lang=language)
    if not tar_filename:
        return False

    print('Extracting {} file...'.format(tar_filename))
    segments_files = extract_segment_files(tar_filename)

    # Iterates over [dev, test, train] files
    for segment_filepath in segments_files:
        # Get links from segments file
        links_dict = get_links_dict(segment_filepath)
        # Define the output path
        output_dir = join( dirname(segment_filepath), 'audio')
        print('Downloading mp3 files from {}...'.format(segment_filepath))
        # Download mp3 files from links_dict
        r = download_mp3_files(links_dict, output_dir)
        if not r:
            print('Erro downloading files.')
            return False

        print('Creating segments list...')
        segments_list, total_files = create_segments_list(segment_filepath, sampling_rate, audio_format, output_dir)

        print('Creating audio segments...')
        if not create_audio_files_from_segments_list(segments_list, total_files, sampling_rate, audio_format):
            return False

        if delete_files:
            remove_mp3_files(segment_filepath)

    print("Ending audio convertion")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--language', default='pt', help='Language to download. Choose one: pt: portuguese, pl: polish, it: italian, sp: spanish, fr: french, du: dutch, ge: german, en: english')
    parser.add_argument('-s', '--sampling_rate', default=22050, help='Sample rate of new dataset')
    parser.add_argument('-f', '--audio_format', default='wav', help='wav or flac')
    parser.add_argument('-d', '--delete_files', action='store_true', default=False)
    args = parser.parse_args()

    execute(args.language, args.sampling_rate, args.audio_format, args.delete_files)

if __name__ == "__main__":
    main()
