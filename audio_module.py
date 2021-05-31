import argparse
from os.path import join, dirname
from audio_tools.audio_converter import create_audio_files_from_segments_list, create_segments_list
from audio_tools.download_mp3_files import get_links_dict, download_mp3_from_dict
from utils.utils import remove_mp3_files
from utils.download_dataset import download_language_dataset, extract_segment_files


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
        output_dir = join( dirname(segment_filepath), 'audio_tools')
        print('Downloading mp3 files from {}...'.format(segment_filepath))
        # Download mp3 files from links_dict
        r = download_mp3_from_dict(links_dict, output_dir)
        if not r:
            print('Erro downloading files.')
            return False

        print('Creating segments list...')
        segments_list, total_files = create_segments_list(segment_filepath, sampling_rate, audio_format, output_dir)

        print('Creating audio_tools segments...')
        if not create_audio_files_from_segments_list(segments_list, total_files, sampling_rate, audio_format):
            return False

        if delete_files:
            remove_mp3_files(segment_filepath)

    print("Ending audio_tools convertion")
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
