import argparse
from os.path import join, dirname
from os import makedirs
from audio_tools.audio_converter import create_audio_files_from_segments_list, create_segments_list
from audio_tools.download_mp3_files import get_links_dict, download_mp3_from_dict
from utils.utils import remove_mp3_files
from utils.download_dataset import download_language_dataset, extract_segment_files


def recreate_cml_dataset(segments_filepath, output_dir, sampling_rate=22050, audio_format='wav', audio_quality=64, force_download=False, force_write=False):
    '''
    Execute convertion pipeline.
    '''

    # Get links from segments file
    links_dict = get_links_dict(segments_filepath, audio_quality)

    print('Downloading mp3 files from {}...'.format(segments_filepath))
    # Download mp3 files from links_dict
    r = download_mp3_from_dict(links_dict, audio_quality, output_dir, force_download)
    if not r:
        print('Error downloading files.')
        return False

    print('Creating segments list...')
    segments_list, total_files = create_segments_list(segments_filepath, sampling_rate, audio_format, audio_quality, output_dir)

    print('Creating audio segments...')
    if not create_audio_files_from_segments_list(segments_list, total_files, sampling_rate, audio_format, force_write):
        return False

    print("Finished audio conversion.")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_segments', default="cml_train_segments_pt.txt", help='CML Segments file')
    parser.add_argument('-s', '--sampling_rate', default=22050, help='Sample rate of new dataset')
    parser.add_argument('-o', '--output_dir', default="mls_portuguese_opus/train/audio", help='Output directory')
    parser.add_argument('-f', '--audio_format', default='wav', help='wav or flac')
    parser.add_argument('-n', '--force_download', action='store_true', default=False)
    parser.add_argument('-w', '--force_write', action='store_true', default=False)
    parser.add_argument('-q', '--audio_quality', default=64, help='64 if sr=22050 or 128 if sr=44100')
    args = parser.parse_args()

    makedirs(args.output_dir, exist_ok=True)
    
    recreate_cml_dataset(args.input_segments, args.output_dir, int(args.sampling_rate), args.audio_format, int(args.audio_quality), args.force_download, args.force_write)

if __name__ == "__main__":
    main()
