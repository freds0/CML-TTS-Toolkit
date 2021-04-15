import argparse
import spacy
from spacy.lang.pt import Portuguese
from spacy.lang.pl import Polish
from tqdm import tqdm
from os.path import join
import time
from time import process_time
from utils.download_dataset import  download_language_dataset, download_books_dataset, extract_transcript_files, extract_book_files
from utils.text_normalization import customized_text_cleaning, portuguese_text_normalize, polish_text_normalize
from text_converter import search_substring
from utils.custom_tokenizer import infix_re
from cleantext import clean
import collections

abbrev2language = {
    'pt': 'portuguese',
    'pl': 'polish',
    'it': 'italian',
    'sp': 'spanish',
    'fr': 'french',
    'du': 'dutch',
    'ge': 'german',
    'en': 'english'
}

def text_cleaning(text):
    text = clean(text,
                      fix_unicode=True,  # fix various unicode errors
                      to_ascii=False,  # transliterate to closest ASCII representation
                      lower=False,  # lowercase text
                      no_line_breaks=True,  # fully strip line breaks as opposed to only normalizing them
                      no_urls=False,  # replace all URLs with a special token
                      no_emails=False,  # replace all email addresses with a special token
                      no_phone_numbers=False,  # replace all phone numbers with a special token
                      no_numbers=False,  # replace all numbers with a special token
                      no_digits=False,  # replace all digits with a special token
                      no_currency_symbols=False,  # replace all currency symbols with a special token
                      no_punct=False,  # remove punctuations
                      replace_with_punct="",  # instead of removing punctuations you may replace them
                      replace_with_url="<URL>",
                      replace_with_email="<EMAIL>",
                      replace_with_phone_number="<PHONE>",
                      replace_with_number="<NUMBER>",
                      replace_with_digit="0",
                      replace_with_currency_symbol="<CUR>",
                      lang="en"  # set to 'de' for German special handling
                      )
    text = customized_text_cleaning(text)
    return text

def get_text_normalization(language_abbrev = 'pt'):
    if language_abbrev == 'pl':
        norm = polish_text_normalize
    else:
        norm = portuguese_text_normalize
    return norm

def get_tokenizer(language_abbrev = 'pt'):
    if language_abbrev == 'pl':
        nlp = Polish()
    else:
        nlp = Portuguese()

    nlp.tokenizer.infix_finditer = infix_re.finditer
    nlp.max_length = 9990000  # or any large value, as long as you don't run out of RAM

    return nlp

def get_transcripts(transcripts_text):
    transcripts_dict = {}
    for line in transcripts_text:
        filename, text = line.split('\t')
        transcripts_dict[filename] = text.strip()
    # Sorting dict by key (filename)
    ordered_transcripts_dict = collections.OrderedDict(sorted(transcripts_dict.items()))
    return ordered_transcripts_dict

def execute(args, language_abbrev='pt', sequenced_text=False, similarity_metric='hamming'):
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

    #transcript_files_list = ['./mls_polish_opus/train/transcripts.txt']
    #books_folder = './lv_text/'
    language = abbrev2language[language_abbrev]

    separator = '|'

    # Defining Tokenizer
    #nlp = get_tokenizer(language_abbrev)

    norm = get_text_normalization(language_abbrev)

    total_similarity = 0.0
    book_id = ''
    # Iterates over [dev, test, train] files
    for transcript_file in transcript_files_list:

        output_filename = transcript_file.split('/')[1]
        output_filename = 'output_' + language + '_' + output_filename + '.csv'
        output_f = open(args.output_file, "w")

        with open(transcript_file) as f:
            transcripts_text = f.readlines()

        start_position = 0

        # Create ordered dict from trascripts list
        transcripts_dict = get_transcripts(transcripts_text)
        # Iterates over each transcription
        for filename, text in tqdm(transcripts_dict.items()):
            print('Processing {}'.format(filename))

            new_book_id = filename.split('_')[1]
            # If it is a new book, updates book_text content
            if new_book_id != book_id:
                book_id = new_book_id

                with open(join(books_folder, language, book_id + '.txt')) as f:
                    book_text = f.read()

                #book_text = norm(book_text)
                # Cleaning complete text
                book_text = text_cleaning(book_text)
                # Tokenizer texts
                #tokens_complete_text = nlp(book_text)

            #tokens_piece_text = nlp(text)

            # The search will continue from the last position, defined by start_position.
            if sequenced_text:
                print('Start position1: {}'.format(start_position))
                text_result, similarity, start_position = search_substring(text, book_text,
                                                                           similarity_metric, start_position)
            # otherwise, the search will start from the beginning of the text, at position zero.
            else:
                text_result, similarity, start_position = search_substring(text, book_text,
                                                                           similarity_metric, 0)
            if not text_result:
                text_result = ''

            # Debug
            print(text.strip())
            print(text_result.strip())
            total_similarity += similarity
            print(similarity)
            line = separator.join([filename.strip(), text.strip(), text_result.strip(), str(similarity) + '\n'])
            output_f.write(line)

        print('Similaridade Media: {}'.format(total_similarity / len(transcripts_text)))
        output_f.close()
        break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-o', '--output_file', default='./output.csv')
    parser.add_argument('-m', '--metric', default='hamming', help='Options: hamming (low accuracy, low computational cost), levenshtein (high accuracy, high computational cost) or ratcliff (average accuracy, average computational cost)')
    parser.add_argument('-l', '--language', default='pt', help='Options: pt (portuguese), pl (polish), it (italian), sp (spanish), fr (french), du (dutch), ge (german), en (english)')
    parser.add_argument('-s', '--sequenced_text', action='store_true', default=False)

    args = parser.parse_args()
    execute(args, args.language, args.sequenced_text, args.metric)

if __name__ == "__main__":
    main()