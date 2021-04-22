import argparse
from glob import glob
from os.path import join, dirname, isfile
from tqdm import tqdm
from text_converter import get_transcripts, text_cleaning, execute_threads_search_substring_by_char, execute_threads_search_substring_by_word

def execute(transcript_file, complete_text_file, search_type, output_file, number_threads):

    output_f = open(output_file, "w")

    with open(transcript_file) as f:
        transcripts_text = f.readlines()

    with open(complete_text_file) as f:
        book_text = f.read()

    # Cleaning complete text
    book_text = text_cleaning(book_text)

    start_position = 0
    separator = '|'
    total_similarity = 0

    # Create ordered dict from trascripts list
    transcripts_dict = get_transcripts(transcripts_text)

    # Iterates over each transcription
    for filename, text in tqdm(transcripts_dict.items()):
        print('Processing {}'.format(filename))

        if search_type == 'char':
            text_result, similarity, start_position = execute_threads_search_substring_by_char(text, book_text, start_position=0, similarity_metric='hamming', total_threads=int(number_threads))
        else:
            text_result, similarity, start_position = execute_threads_search_substring_by_word(text, book_text, start_position=0, similarity_metric='hamming', total_threads=int(number_threads))

        if not text_result:
            text_result = ''
        total_similarity += similarity

        # Debug
        print(text.strip())
        print(text_result.strip())
        print(similarity)
        line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity) + '\n'])
        output_f.write(line)

    print('Mean Similarity: {}'.format(total_similarity / len(transcripts_text)))

    output_f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-m', '--metric', default='hamming', help='Options: hamming (low accuracy, low computational cost), levenshtein (high accuracy, high computational cost) or ratcliff (average accuracy, average computational cost)')
    parser.add_argument('-i', '--input_folder', default='./input/dev')
    parser.add_argument('-c', '--books_folder', default='./lv_text/portuguese/')
    parser.add_argument('-n', '--number_threads', default=4)
    parser.add_argument('-t', '--search_type', default='word', help='Options: word or char')
    parser.add_argument('-s', '--sequenced_text', action='store_true', default=False)

    args = parser.parse_args()
    
    for transcript_file in glob(join(args.base_dir, args.input_folder) + '/**/**/transcripts.txt'):
        output_folder = dirname(transcript_file)
        book_file = transcript_file.split('/')[-2]
        output_filepath = join(output_folder, 'output.txt')
        complete_text_file = join(args.base_dir, args.books_folder, book_file + '.txt')
        # Verify if folder alread converted
        if isfile(output_filepath):
            with open(output_filepath) as f:
                content_output = f.readlines()
            with open(transcript_file) as f:
                content_input = f.readlines()
            if len(content_output) == len(content_input):
                print('{} já existe!'.format(output_filepath))
                continue
        execute(transcript_file, complete_text_file, args.search_type, output_filepath, int(args.number_threads))

if __name__ == "__main__":
    main()