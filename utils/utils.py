from os.path import join, dirname
from os import remove
from glob import glob

def get_filepath_from_link(link, output_path):
    '''
    Get filename and filepath from link.
    '''
    link = link.replace('64', '128')
    filename = link.split('/')[-1]
    filepath = join(output_path, filename)
    return filepath

def remove_mp3_files(segment_filepath):
    '''
    Remove mp3 files.
    '''
    mp3_filelist = glob(dirname(segment_filepath) + '/audio/**/**/*.mp3')
    for mp3_file in mp3_filelist:
        remove(mp3_file)