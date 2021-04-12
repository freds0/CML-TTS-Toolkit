#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dado a transcricao de um arquivo, busca a frase mais proxima dentro de um texto completo.
#
# (C) 2021 Frederico Oliveira, UFMT
# Released under GNU Public License (GPL)
# email fred.santos.oliveira@gmail.com
#

import argparse
import spacy
from spacy.lang.pt import Portuguese
from custom_tokenizer import infix_re
import string
import textdistance
from tqdm import tqdm
import re
import os
import tarfile
import urllib.request
import progressbar
from text_normalization import text_normalize

import time
from time import process_time

PUNCTUATION = string.punctuation+ '—'
def remove_punctuations(text):

    # Remove punctuations
    text = text.translate(str.maketrans("","", PUNCTUATION)).strip()
    return text

def preprocess_string(text):
    '''
    Auxiliar fucntion. Convert text to lower case, remove the punctuation and spaces. After preprocessing you will have the text as a single string, with no spaces between words.

        Parameters:
        text (str): normal text.

        Returns:
        String: returns text preprocessed.
    '''
    # Convert to lower
    text = text.lower()
    text = remove_punctuations(text)
    # Remove blank spaces
    text = text.replace(" ", "")
    # Remove newlines
    text = re.sub('\n', '', text)
    return text


def compare_word_by_word(substring, complete_string, similarity_metric = 'hamming'):
    '''
    Auxiliar fucntion. Checks word by word if a substring is contained in a complete text, ignoring the punctuation and capital letters.

        Parameters:
        substring (str): phrase to be searched for in the complete text.
        complete_text (str): complete text that has a phrase similar to the substring.

        Returns:
        String: returns the phrase if it found a similar phrase, otherwise it returns False
    '''
    if similarity_metric == 'levenshtein':
        min_similarity = 0.5 # minimal similarity between the words tested with levenshtein
    else:
        min_similarity = 0.3 # minimal similarity between the words tested with hamming

    i = 0 # substring index iterator
    j = 0 # complete_string index iterator
    start = 0

    # i iterate over the variable "substring" and j iterate over the variable "complete_string"
    while i < len(substring) and j < (len(complete_string)):

        # Necessary when it has a punctuation at begining
        if i == 0 and complete_string[j].text in PUNCTUATION:
            j += 1
            start += 1
            continue

        # Ignores punctuation at substring
        if substring[i].text in PUNCTUATION:
            i += 1
            continue

        # Ignores punctuation at complete_string
        if complete_string[j].text in PUNCTUATION:
            j += 1
            continue

        # Preprocesses the two words to calculate the similarity
        word1 = substring[i].text.lower()
        word2 = complete_string[j].text.lower()
        
        if similarity_metric == 'levenshtein':
            similarity = textdistance.levenshtein.normalized_similarity(word1, word2)
        else:
            similarity = textdistance.hamming.normalized_similarity(word1, word2)

        # word1 does not match the word2, but it still returns the found string not including word2 . 
        if similarity < min_similarity:
             return complete_string[start : j]

        i += 1
        j += 1

    return complete_string[start : j]


def find_substring_by_word(substring, complete_text, similarity_metric = 'hamming', start_position = 0):

    length_complete_text = len(complete_text)
    length_substring     = len(substring)

    best_similarity = 0.0
    best_substring_found = False
    start_tmp = start_position

    # Iterates over the complete text from position zero, increasing the initial position.
    for start in range(start_position, length_complete_text - length_substring):

        # Defines the starting position in which to search for substring
        complete_text_tmp = complete_text[start :]

        # Performs the comparison of each word in the sequence
        substring_found = compare_word_by_word(substring, complete_text_tmp, similarity_metric)

        # In this comparison it is better to use levenshtein distance because it has better accuracy.
        similarity = textdistance.levenshtein.normalized_similarity(
                remove_punctuations(substring.text.lower()), 
                remove_punctuations(substring_found.text.lower())
        )
        # Updates the best string found.
        if similarity > best_similarity:
            best_similarity = similarity
            best_substring_found = substring_found.text
        
        # Break if it find a phrase with minimal similarity of words. Comment if you desire search for all text
        if best_similarity > 0.9999:
            start_tmp = start
            break

    return best_substring_found, best_similarity, start_tmp

def compare_char_by_char(substring, complete_string):
    '''
    Auxiliar fucntion. Checks word by word if a substring is contained in a complete text, ignoring the punctuation and capital letters.

        Parameters:
        substring (str): phrase to be searched for in the complete text.
        complete_text (str): complete text that has a phrase similar to the substring.

        Returns:
        String: returns the phrase if it found a similar phrase, otherwise it returns False
    '''

    j = int(0.9 * len(substring))
  
    min_similarity = 0.5
    best_similarity = 0.0

    while j < len(complete_string):   

        # Ignores punctuation at complete_string
        if complete_string[j].text in PUNCTUATION:
            j += 1
            continue

        # Transforms the string into a single string without spaces 
        sentence1 = preprocess_string(substring.text)
        sentence2 = preprocess_string(complete_string[:j].text)

        similarity = textdistance.hamming.normalized_similarity(sentence1, sentence2)

        if similarity < min_similarity:
             return False

        if similarity > best_similarity:
            best_similarity = similarity
            j += 1

        else:
            j -= 1
            break

    # Necessary when it has a punctuation at begining
    i = 0
    while complete_string[i].text in PUNCTUATION:
        i += 1

    return complete_string[i:j]

def find_substring_by_char(substring, complete_text, start_position = 0):
    length_complete_text = len(complete_text)
    length_substring     = len(substring)

    best_similarity        = 0.0
    best_substring_found   = False
    start                  = start_position
    extra_words            = 10 # it is necessary to add extra words, because the punctuation is also counted.
    # Iterates over the complete text from position zero, increasing the initial position.
    for start in range(start_position, length_complete_text - length_substring):

        # Defines the starting position in which to search for substring
        complete_text_tmp = complete_text[start : start + length_substring + extra_words]

        # Performs the comparison of the two sentences, inserting each word in the complete_text_tmp
        substring_found = compare_char_by_char(substring, complete_text_tmp)

        if substring_found:
            # In this comparison it is better to use levenshtein distance because it has better accuracy.
            similarity = textdistance.levenshtein.normalized_similarity(preprocess_string(substring.text), preprocess_string(substring_found.text))

            # Updates the best string found.
            if similarity > best_similarity:
                best_similarity = similarity
                best_substring_found = substring_found.text
    
            # Break if it find a phrase with minimal similarity of words. Comment if you desire search for all text
            if best_similarity > 0.9999:
                break

    return best_substring_found, best_similarity, start

def find_substring(substring, complete_text, similarity_metric = 'hamming', start_position = 0):
    '''
    Finds the phrase closest to a substring within a complete text, ignoring the punctuation and capital letters.

        Parameters:
        substring (str): phrase to be searched for in the complete text.
        complete_text (str): complete text that has a phrase similar to the substring.

        Returns:
        String: returns the phrase if it found a similar phrase, otherwise it returns False
    '''
    
    print('Searching by word...')
    char_similarity = 0.0
    word_similarity = 0.0

    word_string_result, word_similarity, new_start_position = find_substring_by_word(substring, complete_text, similarity_metric, start_position)

    if word_similarity < 0.9999:
        print('Searching by char...')
        start_position = 0
        char_string_result, char_similarity, new_start_position = find_substring_by_char(substring, complete_text, start_position)

    if word_similarity > char_similarity:
        string_result = word_string_result
        similarity = word_similarity
    else:
        string_result = char_string_result
        similarity = char_similarity
    '''
    print('Searching by char...')
    string_result, similarity, new_start_position = find_substring_by_char(substring, complete_text, start_position)
    '''
    if string_result:
        start_position += new_start_position

    return string_result, similarity, new_start_position

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

def download_language_dataset(lang = 'pt'):
    '''
    Download datasets
    '''
    # Books information
    url = 'https://dl.fbaipublicfiles.com/mls/lv_text.tar.gz'

    books_filename = url.split('/')[-1]
    if os.path.isfile(books_filename):
        print('File {} exists!'.format(books_filename))

    else:
        # Download books information
        urllib.request.urlretrieve(url, books_filename, MyProgressBar())  

    # Choose dataset
    if lang == 'pt':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_portuguese_opus.tar.gz'
        language = 'portuguese'
    elif lang == 'po':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_polish_opus.tar.gz'
        language = 'polish'
    elif lang == 'it':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_italian_opus.tar.gz'        
        language = 'italian'
    elif lang == 'sp':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_spanish_opus.tar.gz'
        language = 'spanish'
    elif lang == 'fr':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_french_opus.tar.gz'
        language = 'french'
    elif lang == 'du':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_dutch_opus.tar.gz'
        language = 'dutch'
    elif lang == 'ge':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_german_opus.tar.gz'   
        language = 'german'    
    elif lang == 'en':
        url = 'https://dl.fbaipublicfiles.com/mls/mls_english_opus.tar.gz'
        language = 'english'  
    else:
        print('Error: invalid language {}.'.format(lang))        
        return False

    transcripts_filename = url.split('/')[-1]
    if os.path.isfile(transcripts_filename):
        print('File {} exists!'.format(transcripts_filename))

    else:
        # Download transcripts information
        urllib.request.urlretrieve(url, transcripts_filename, MyProgressBar())  

    return transcripts_filename, books_filename, language

def extract_tar_file(tar_filename_books, tar_filename_transcripts):
    '''
    Extract segments.txt file from tar.gz
    '''

    # Extract transcripts
    basename   = os.path.basename(tar_filename_transcripts).split('.')[0]
    dev_trans_file   = os.path.join(basename, 'dev/transcripts.txt')
    test_trans_file  = os.path.join(basename, 'test/transcripts.txt')
    train_trans_file = os.path.join(basename, 'train/transcripts.txt')

    transcripts_files = [
        dev_trans_file,
        test_trans_file,
        train_trans_file
    ]

    if os.path.isfile(dev_trans_file) and os.path.isfile(test_trans_file) and os.path.isfile(train_trans_file):
        print('Transcripts already extracted!')
        #return transcripts_files

    '''
    my_tar = tarfile.open(tar_filename_transcripts)
    my_tar.extract(dev_trans_file,'./')
    my_tar.extract(test_trans_file,'./')
    my_tar.extract(train_trans_file,'./')
    my_tar.close()
    '''
    #return transcripts_files

    # Extract books
    basename  = os.path.basename(tar_filename_books).split('.')[0]

    if os.path.isdir(basename):
        print('File {} already extracted!'.format(basename))
        #return basename

    '''
    my_tar = tarfile.open(tar_filename_books)
    my_tar.extractall()
    my_tar.close()
    '''
    return transcripts_files

def executar(args, language = 'pt', sequenced_text = False, similarity_metric = 'hamming'):

    '''
    Execute convertion pipeline.
    '''

    '''
    print('Downloading {} dataset tar.gz file...'.format(language))
    transcripts_tar_filename, books_tar_filename, language = download_language_dataset(lang=language)
    if not transcripts_tar_filename or not books_tar_filename:
        return False

    print('Extracting files {} {}...'.format(transcripts_tar_filename, books_tar_filename))
    transcript_files_list = extract_tar_file(books_tar_filename, transcripts_tar_filename)
    '''

    transcript_files_list = [
        './transcript_teste.txt'
    ]
    language = 'portuguese'

    separator = '|'

    nlp = Portuguese()
    nlp.tokenizer.infix_finditer = infix_re.finditer
    nlp.max_length = 9990000 #or any large value, as long as you don't run out of RA

    # Metrics
    begin_cpu_time = process_time() 
    total_similarity = 0    
    begin_execution_time = time.time()

    for transcript_file in transcript_files_list:

        output_f = open(args.output_file, "w")

        with open(transcript_file) as f:
            transcripts_text = f.readlines()
      
        start_position = 0
        total_similarity = 0    

        for line in tqdm(transcripts_text): 

            filename, text = line.split('\t')
            print('Processing {}'.format(filename))
    
            book_id = filename.split('_')[1]

            with open(os.path.join('./lv_text', language, book_id + '.txt')) as f:
                book_text = f.read()

            book_text = text_normalize(book_text)

            tokens_complete_text = nlp(book_text)
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
            output_f.write(line)

        break
    output_f.close()

    end_cpu_time = process_time() 
    total_secs = round(time.time() - begin_execution_time)

    print('Tempo CPU find_substring: {}'.format(end_cpu_time - begin_cpu_time))

    print("Tempo total: {} min".format(total_secs / 60))

    print("Similaridade Media: {}".format(total_similarity / len(content_piece_text)))

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
    parser.add_argument('-c', '--complete_file', default='./8708_pre.txt')
    parser.add_argument('-p', '--piece_file', default='./transcripts_8708.txt')
    parser.add_argument('-o', '--output_file', default='./output.csv')
    parser.add_argument('-m', '--metric', default='hamming', help='Two options: hamming or levenshtein')
    parser.add_argument('-l', '--language', default='pt', help='Options: pt (portuguese), po (polish), it (italian), sp (spanish), fr (french), du (dutch), ge (german), en (english)')
    parser.add_argument('-s', '--sequenced_text', action='store_true', default=False)

    args = parser.parse_args()
    executar(args, args.language, args.sequenced_text, args.metric)

if __name__ == "__main__":
    main()
