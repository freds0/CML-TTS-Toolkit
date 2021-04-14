#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dado a transcricao de um arquivo, busca a frase mais proxima dentro de um texto completo.
#
# (C) 2021 Frederico Oliveira, UFMT
# Released under GNU Public License (GPL)
# email fred.santos.oliveira@gmail.com
#
import string
import textdistance
from tqdm import tqdm
import re

PUNCTUATION = string.punctuation + '—'
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
    return text.strip()


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
        if best_similarity > 0.99:
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
    length_substring = len(substring)

    best_similarity = 0.0
    best_substring_found = False
    start = start_position
    extra_words = 10 # it is necessary to add extra words, because the punctuation is also counted.
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
            if best_similarity >= 0.99:
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

    if word_similarity < 0.99:
        print('Searching by char...')
        start_position = 0
        char_string_result, char_similarity, new_start_position = find_substring_by_char(substring, complete_text, start_position)

    if word_similarity > char_similarity:
        string_result = word_string_result
        similarity = word_similarity
    else:
        string_result = char_string_result
        similarity = char_similarity

    if string_result:
        start_position += new_start_position

    return string_result, similarity, new_start_position


