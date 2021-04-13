import argparse
import spacy
from spacy.lang.pt import Portuguese
from tqdm import tqdm
from os.path import join
import time
from time import process_time
from utils.download_dataset import  download_language_dataset, download_books_dataset, extract_transcript_files, extract_book_files
from utils.text_normalization import text_normalize
from text_converter import find_substring
from utils.custom_tokenizer import infix_re

abbrev2language = {
    'pt': 'portuguese',
    'po': 'polish',
    'it': 'italian',
    'sp': 'spanish',
    'fr': 'french',
    'du': 'dutch',
    'ge':'german',
    'en':'english'
}

def executar(args, language_abbrev='pt', sequenced_text=False, similarity_metric='hamming'):
    '''
    Execute convertion pipeline.
    '''

    print('Downloading {} dataset tar.gz file...'.format(language_abbrev))
    transcripts_tar_filename =  download_language_dataset(lang=language_abbrev)
    if not transcripts_tar_filename:
        return False

    print('Extracting files {}...'.format(transcripts_tar_filename))
    transcript_files_list = extract_transcript_files(transcripts_tar_filename)

    print('Downloading {} books tar.gz file...'.format(language_abbrev))
    books_tar_filename = download_books_dataset(lang=language_abbrev)

    print('Extracting files {}...'.format(books_tar_filename))
    books_folder = extract_book_files(books_tar_filename)

    language = abbrev2language(language_abbrev)

    separator = '|'

    # Defining Portuguese Tokenizer
    nlp = Portuguese()
    nlp.tokenizer.infix_finditer = infix_re.finditer
    nlp.max_length = 9990000  # or any large value, as long as you don't run out of RAM


    for transcript_file in transcript_files_list:

        output_f = open(args.output_file, "w")

        with open(transcript_file) as f:
            transcripts_text = f.readlines()

        start_position = 0
        for line in tqdm(transcripts_text):

            filename, text = line.split('\t')
            print('Processing {}'.format(filename))

            book_id = filename.split('_')[1]

            with open(join(books_folder, language, book_id + '.txt')) as f:
                book_text = f.read()

            # Cleaning complete text
            book_text = text_normalize(book_text)
            # Tokenizer texts
            tokens_complete_text = nlp(book_text)
            tokens_piece_text = nlp(text)

            # The search will continue from the last position, defined by start_position.
            if sequenced_text:
                print('Start position: {}'.format(start_position))
                text_result, similarity, start_position = find_substring(tokens_piece_text, tokens_complete_text,
                                                                         similarity_metric, start_position)
            # otherwise, the search will start from the beginning of the text, at position zero.
            else:
                text_result, similarity, start_position = find_substring(tokens_piece_text, tokens_complete_text,
                                                                         similarity_metric, 0)
            if not text_result:
                text_result = ''

            print(text.strip())
            print(text_result.strip())

            line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity) + '\n'])
            output_f.write(line)
        break
    output_f.close()

    '''
    #nlp = spacy.load('pt_core_news_sm')
    nlp = Portuguese()
    nlp.tokenizer.infix_finditer = infix_re.finditer
    #nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 9990000 #or any large value, as long as you don't run out of RA

    with open(args.complete_file) as f:
        complete_text = f.read()

    with open(args.piece_file) as f:
        content_piece_text = f.readlines()

    f = open(args.output_file, "w")

    separator = '|'
    complete_text = re.sub('\n', '', complete_text)

    start_position = 0
    # Metrics
    begin_cpu_time = process_time() 
    total_similarity = 0    
    begin_execution_time = time.time()

    for line in tqdm(content_piece_text):    
        filename, text = line.split('\t')
        print('Processing {}'.format(filename))

        tokens_complete_text = nlp(complete_text)
        tokens_piece_text    = nlp(text)

        # the search will continue from the last position, defined by  start_position.
        if sequenced_text:
            print('Start position: {}'.format(start_position))
            text_result, similarity, start_position = find_substring(tokens_piece_text, tokens_complete_text, similarity_metric, start_position)
        # otherwise, the search will start from the beginning of the text, at position zero.
        else:
            text_result, similarity, start_position = find_substring(tokens_piece_text, tokens_complete_text, similarity_metric, 0)

        if not text_result:
            text_result = '' 

        print(text.strip())
        print(text_result.strip())
        print(similarity)
        total_similarity +=  similarity

        line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity) + '\n'])
        f.write(line)

    f.close()
    end_cpu_time = process_time() 
    total_secs = round(time.time() - begin_execution_time)


    print('Tempo CPU find_substring: {}'.format(end_cpu_time - begin_cpu_time))

    print("Tempo total: {} min".format(total_secs / 60))

    print("Similaridade Media: {}".format(total_similarity / len(content_piece_text)))

    '''



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-c', '--complete_file', default='./3702_pre.txt')
    parser.add_argument('-p', '--piece_file', default='./transcripts_3702.txt')
    parser.add_argument('-o', '--output_file', default='./output.csv')
    parser.add_argument('-m', '--metric', default='hamming', help='Two options: hamming or levenshtein')
    parser.add_argument('-l', '--language', default='pt', help='Options: pt (portuguese), po (polish), it (italian), sp (spanish), fr (french), du (dutch), ge (german), en (english)')
    parser.add_argument('-s', '--sequenced_text', action='store_true', default=False)

    args = parser.parse_args()
    executar(args, args.language, args.sequenced_text, args.metric)

if __name__ == "__main__":
    main()