import argparse
from tqdm import tqdm
from os.path import join, dirname
from os import makedirs
import collections

def get_transcripts(transcripts_text):
    transcripts_dict = {}
    for line in transcripts_text:
        filename, text = line.split('\t')
        transcripts_dict[filename] = text.strip()
    # Sorting dict by key (filename)
    ordered_transcripts_dict = collections.OrderedDict(sorted(transcripts_dict.items()))
    return ordered_transcripts_dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input_file', default='./mls_portuguese_opus/dev/transcripts.txt')
    parser.add_argument('-o', '--output_folder', default='./input')
    args = parser.parse_args()

    # Load input file
    input_file = join(args.base_dir, args.input_file)

    folder0 = args.input_file.split('/')[2]

    with open(input_file) as f:
        input_text = f.readlines()  

    # Create ordered dict from trascripts list
    transcripts_dict = get_transcripts(input_text)

    # Iterates over each transcription
    for filename, text in tqdm(transcripts_dict.items()):
        folder1, folder2, fileid = filename.split('_')
        output_filepath = join(args.output_folder, folder0, folder1, folder2, 'transcripts.txt')

        makedirs(dirname(output_filepath), exist_ok=True)    
        output_f = open(output_filepath, "a")   

        line = '\t'.join([filename, text + '\n'])
        output_f.write(line)
    
    output_f.close()

if __name__ == "__main__":
    main()