import argparse
from glob import glob
from os.path import join, dirname, isfile
from tqdm import tqdm
from text_tools.search_substring_with_threads import get_transcripts, text_cleaning, execute_threads_search_substring_by_char, execute_threads_search_substring_by_word
from text_tools.create_structure_folders import change_structure_folders
from utils.download_dataset import  download_language_dataset, download_books_dataset, extract_transcript_files, extract_book_files
from utils.utils import abbrev2language


def search_substring_with_punctuation(language_abbrev, transcript_file, complete_text_file, search_type, output_file, number_threads):
    '''
    Perform substring search for each substring of file transcript_file in a file complete_text_file
    '''

    with open(transcript_file) as f:
        transcripts_text = f.readlines()

    with open(complete_text_file) as f:
        book_text = f.read()

    output_f = open(output_file, "w")

    # Cleaning complete text_tools
    book_text = text_cleaning(book_text)

    start_position = 0
    separator = '|'
    total_similarity = 0

    # Create ordered dict from transcripts list
    transcripts_dict = get_transcripts(transcripts_text)

    # Iterates over each transcription
    for filename, text in tqdm(transcripts_dict.items()):
        print('Processing {}'.format(filename))

        if search_type == 'char':
            text_result, similarity, start_position = execute_threads_search_substring_by_char(language_abbrev, text, book_text, start_position=0, similarity_metric='hamming', total_threads=int(number_threads))
        else:
            text_result, similarity, start_position = execute_threads_search_substring_by_word(language_abbrev, text, book_text, start_position=0, similarity_metric='hamming', total_threads=int(number_threads))

        if not text_result:
            text_result = ''
        total_similarity += similarity

        # Some information
        print(text.strip())
        print(text_result.strip())
        print(similarity)
        # Write to file
        line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity) + '\n'])
        output_f.write(line)

    print('Mean Similarity: {}'.format(total_similarity / len(transcripts_text)))
    output_f.close()


def keep_searching_substring_with_punctuation(language_abbrev, transcript_file, complete_text_file, search_type, output_file, number_threads):
    '''
    Perform substring search only for files with low similarity.
    '''

    with open(transcript_file) as f:
        transcripts_text = f.readlines()

    with open(complete_text_file) as f:
        book_text = f.read()

    output_f = open(output_file, "w")

    # Cleaning complete text_tools
    book_text = text_cleaning(book_text)

    start_position = 0
    separator = '|'
    total_similarity = 0

    # Iterates over each transcription
    for line in tqdm(transcripts_text):
        filename, text, text_result, similarity = line.split('|')

        if float(similarity) > 0.9:
            line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity.strip()) + '\n'])
            output_f.write(line)
            continue

        print('Processing {}'.format(filename))

        if search_type == 'char':
            text_result, similarity, start_position = execute_threads_search_substring_by_char(language_abbrev, text, book_text, start_position=0, similarity_metric='hamming', total_threads=int(number_threads))
        else:
            text_result, similarity, start_position = execute_threads_search_substring_by_word(language_abbrev, text, book_text, start_position=0, similarity_metric='hamming', total_threads=int(number_threads))

        if not text_result:
            text_result = ''
        total_similarity += similarity

        # Some information
        print(text.strip())
        print(text_result.strip())
        print(similarity)
        # Write to file
        line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity) + '\n'])
        output_f.write(line)

    print('Mean Similarity: {}'.format(total_similarity / len(transcripts_text)))

    output_f.close()


def execution_text_convertion_pipeline(language_abbrev, input_folder, books_folder, search_type, threads_number):

    language = abbrev2language[language_abbrev]
    print('Downloading {} dataset tar.gz file...'.format(language_abbrev))
    transcripts_tar_filename = download_language_dataset(lang=language_abbrev)
    if not transcripts_tar_filename:
        return False

    print('Extracting files {}...'.format(transcripts_tar_filename))
    transcript_files_list = extract_transcript_files(transcripts_tar_filename)

    print('Downloading {} books tar.gz file...'.format(language_abbrev))
    books_tar_filename = download_books_dataset(lang=language_abbrev)

    print('Extracting files {}...'.format(books_tar_filename))
    books_folder = extract_book_files(books_tar_filename)

    # Run folder restructuring
    for transcript_file in transcript_files_list:
        print('Executing {} file'.format(transcript_file))
        output_folder = dirname(transcript_file)
        change_structure_folders(transcript_file, output_folder)

    # Run substring search in books
    for transcript_file in glob(output_folder + '/**/**/transcripts.txt'):
        # Defining output filepath
        output_filepath = join(dirname(transcript_file), 'output_search.txt')
        # Defining text book filepath
        book_file = transcript_file.split('/')[-2]
        complete_text_file = join(books_folder, language, book_file + '.txt')

        # Verify if search was already done
        if isfile(output_filepath):
            with open(output_filepath) as f:
                content_output = f.readlines()

            with open(transcript_file) as f:
                content_input = f.readlines()

            if len(content_output) == len(content_input):
                # Perform substring search only for files with low similarity
                keep_searching_substring_with_punctuation(language_abbrev, output_filepath, complete_text_file, search_type, output_filepath, int(threads_number))
                continue
        # First execution of search
        search_substring_with_punctuation(language_abbrev, transcript_file, complete_text_file, search_type, output_filepath, int(threads_number))

    # Insert punctuation of the found substring in the transcript text
    for metadata_search in tqdm(glob(output_folder + '/**/**/output_search.txt' )):
        insert_punctuation_on_substring(metadata_search, output_filepath)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-l', '--language', default='pt',
                        help='Options: pt (portuguese), pl (polish), it (italian), sp (spanish), fr (french), du (dutch), ge (german), en (english)')
    parser.add_argument('-m', '--metric', default='hamming', help='Options: hamming (low accuracy, low computational cost), levenshtein (high accuracy, high computational cost) or ratcliff (average accuracy, average computational cost)')
    parser.add_argument('-i', '--input_folder', default='./input/dev')
    parser.add_argument('-c', '--books_folder', default='./lv_text/portuguese/')
    parser.add_argument('-n', '--threads_number', default=4)
    parser.add_argument('-t', '--search_type', default='word', help='Options: word or char')
    parser.add_argument('-s', '--sequenced_text', action='store_true', default=False)

    args = parser.parse_args()

    input_folder = join(args.base_dir, args.input_folder)
    books_folder = join(args.base_dir, args.books_folder)

    execution_text_convertion_pipeline(args.language, input_folder, books_folder, args.search_type, args.threads_number)


if __name__ == "__main__":
    main()