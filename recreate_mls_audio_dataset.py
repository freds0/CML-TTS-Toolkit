#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# (C) 2021 Frederico Oliveira fred.santos.oliveira@gmail.com
# Released under GNU Public License (GPL)
# Adapted from https://gist.github.com/keithito/771cfc1a1ab69d1957914e377e65b6bd from Keith Ito: kito@kito.us
import argparse
import os
import json
import urllib.request
import progressbar
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm
import tarfile
import glob

class Segment:
    '''
    Linked segments Class
    '''
    def __init__(self, begin, end, filesource, filepath):
        self.begin = begin
        self.end = end
        self.next = None
        self.filesource = filesource
        self.filepath = filepath
        self.gap = 0 # gap between segments (current and next)

    def set_next(self, next):
        self.next = next
        self.gap = next.begin - self.end

    def set_filename_and_id(self, filename, id):
        self.filename = filename
        self.id = id

    def merge_from(self, next):
        # merge two segments (current and next)
        self.next = next.next
        self.gap = next.gap
        self.end = next.end

    def duration(self, sample_rate):
        return (self.end - self.start - 1) / sample_rate


class MyProgressBar():
    '''
    Progress Bar for Download. 
    Source: https://stackoverflow.com/questions/37748105/how-to-use-progressbar-module-with-urlretrieve
    '''
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

def get_filename_filepath(link, output_path):
    '''
    Get filename and filepath from link.
    '''
    link = link.replace('64', '128')
    filename = link.split('/')[-1]
    filepath = os.path.join(output_path, filename)

    return filename, filepath

def download_mp3_files(segments_filepath, output_dir):
    '''
    Given a list of links, downloads mp3 files at 64kbs.
    '''
    with open(segments_filepath) as f :
        content_data = f.readlines()

        total = len(content_data)
        for i, line in enumerate(tqdm(content_data)):
            filename, link, _, _ = line.strip().split("\t")

            # Getting complete filepath
            folder1, folder2, fileid = filename.split('_')
            output_path = os.path.join(output_dir, folder1, folder2)
            os.makedirs(output_path, exist_ok=True)

            # Downloading file. 
            mp3_filename, mp3_filepath = get_filename_filepath(link, output_path)
            #print('Download {} / {} file: {}'.format(i, total, mp3_filename))
            if not (os.path.isfile(mp3_filepath)):
                #urllib.request.urlretrieve(link, mp3_filepath, MyProgressBar())          
                urllib.request.urlretrieve(link, mp3_filepath)          

    return True

def create_segments_list(segments_filepath, sampling_rate = 22050, audio_format = 'wav', output_dir = './'):
    '''
    Creates a linked segment list from a file.
    '''
    extension_file = '.wav' if audio_format == 'wav' else '.flac'
    head = None
    with open(segments_filepath) as f :
        content_data = f.readlines()

        for line in tqdm(content_data):

            filename, link, begin, end = line.strip().split("\t")
            # Get files path
            folder1, folder2, fileid = filename.split('_')
            output_path = os.path.join(output_dir, folder1, folder2)
            # Must be like download_mp3_files function
            _, mp3_filepath = get_filename_filepath(link, output_path)
            output_filepath = os.path.join(output_path, filename + extension_file)

            # Verify sample rate
            info = mediainfo(mp3_filepath)
            if int(info['sample_rate']) < int(sampling_rate):
                print('Ignoring {} sr = {}'.format(mp3_filepath, info['sample_rate']))
                continue;

            # Creating segment
            begin = float(begin)*1000
            end = float(end)*1000

            # Build a segment list
            segment = Segment(begin, end, mp3_filepath, output_filepath)
            if head is None:
                head = segment
            else:
                prev.set_next(segment)
            prev = segment

    return head, len(content_data)

def create_audio_files_from_segments_list(head_list, total_files, sampling_rate = 22050, audio_format = 'wav'):
    '''
    Creates audio segments from a linked segment list.
    '''
    curr = head_list
    i = 1

    pbar = tqdm(total=total_files)

    while curr is not None:
        audio_file = curr.filesource
        begin = curr.begin
        end = curr.end
        filepath = curr.filepath
        sound = AudioSegment.from_file(audio_file, frame_rate=sampling_rate, channels=1)
        audio_segment = sound[begin:end]
        #print("Exporting {}".format(filepath))
        try:
            if audio_format == 'wav':
                audio_segment.export(filepath, format = "wav")
            else:
                audio_segment.export(filepath, format = "flac")

        except IOError:
          print("Error: Writing audio file {} problem.".format(filepath))
          return False
        else:
            curr = curr.next
            i += 1
        pbar.update(1)

    pbar.close()
    return True

def download_language_dataset(lang='pt'):
    '''
    Download datasets
    '''

    if lang == 'pt':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_portuguese_opus.tar.gz'
    elif lang == 'po':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_polish_opus.tar.gz'
    elif lang == 'it':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_italian_opus.tar.gz'        
    elif lang == 'sp':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_spanish_opus.tar.gz'
    elif lang == 'fr':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_french_opus.tar.gz'
    elif lang == 'du':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_dutch_opus.tar.gz'
    elif lang == 'ge':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_german_opus.tar.gz'       
    elif lang == 'en':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_english_opus.tar.gz'
    else:
        print('Error: invalid language {}.'.format(lang))        
        return False

    filename = url.split('/')[-1]
    if os.path.isfile(filename):
        print('File {} exists!'.format(filename))

    else:
        urllib.request.urlretrieve(url, filename, MyProgressBar())  

    return filename

def extract_tar_file(tar_filename):
    '''
    Extract segments.txt file from tar.gz
    '''
    basename   = os.path.basename(tar_filename).split('.')[0]
    dev_file   = os.path.join(basename, 'dev/segments.txt')
    test_file  = os.path.join(basename, 'test/segments.txt')
    train_file = os.path.join(basename, 'train/segments.txt')
    dev_trans_file   = os.path.join(basename, 'dev/transcripts.txt')
    test_trans_file  = os.path.join(basename, 'test/transcripts.txt')
    train_trans_file = os.path.join(basename, 'train/transcripts.txt')

    segments_files = [
        dev_file,
        test_file,
        train_file
    ]

    if os.path.isfile(dev_file) and os.path.isfile(test_file) and os.path.isfile(train_file):
        print('Segments files exists!')
        return segments_files

    my_tar = tarfile.open(tar_filename)
    my_tar.extract(dev_file,'./')
    my_tar.extract(test_file,'./')
    my_tar.extract(train_file,'./')
    my_tar.extract(dev_trans_file,'./')
    my_tar.extract(test_trans_file,'./')
    my_tar.extract(train_trans_file,'./')
    my_tar.close()

    return segments_files


def remove_files(segments_filepath):
    '''
    Remove mp3 files.
    '''
    mp3_filelist = glob.glob(os.path.dirname(segments_filepath) + '/audio/**/**/*.mp3')
    for mp3_file in mp3_filelist:
        os.remove(mp3_file)


def execute(language, sampling_rate = 22050, audio_format = 'wav', delete_files = False):
    '''
    Execute convertion pipeline.
    '''
    print('Downloading {} dataset tar.gz file...'.format(language))
    tar_filename = download_language_dataset(lang=language)
    if not tar_filename:
        return False

    print('Extracting {} file...'.format(tar_filename))
    segments_files = extract_tar_file(tar_filename)

    for segments_filepath in segments_files:
        output_dir =  os.path.join(os.path.dirname(segments_filepath), 'audio')
        print('Downloading mp3 files from {}...'.format(segments_filepath))
        r = download_mp3_files(segments_filepath, output_dir)
        r = True
        if not r:
            print('Erro downloading files.')
            return False

        print('Creating segments list...')
        segments_list, total_files = create_segments_list(segments_filepath, sampling_rate, audio_format, output_dir)

        print('Creating audio segments...')
        if not create_audio_files_from_segments_list(segments_list, total_files, sampling_rate, audio_format):
            return False

        if delete_files:
            remove_files(segments_filepath)

    print("End")

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default='pt', help='Language to download')
    parser.add_argument('--sampling_rate', default=22050, help='Sample rate of new dataset')
    parser.add_argument('--audio_format', default='wav', help='wav or flac')
    parser.add_argument('--delete_files', action='store_true', default=False)
    args = parser.parse_args()

    execute(args.language, args.sampling_rate, args.audio_format, args.delete_files)


if __name__ == "__main__":
    main()
