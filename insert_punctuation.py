import argparse
import csv
import glob
from os.path import join, dirname
from spacy.lang.pt import Portuguese
from utils.custom_tokenizer import infix_re
import textdistance

nlp = Portuguese()
nlp.tokenizer.infix_finditer = infix_re.finditer


def find_bigram(bigram, text):

    best = 0
    index = False
    words_list = text.split(' ')

    for i in range(1, len(words_list)):
        w0, w1 = bigram
        lev0 = textdistance.ratcliff_obershelp.normalized_similarity(w0, words_list[i-1])
        lev1 = textdistance.ratcliff_obershelp.normalized_similarity(w1, words_list[i])
        if lev0 + lev1 > best:
            best = lev0 + lev1
            index = i

    return index


def correct_punctuation(text_clean, text_punc):

    punctuation = [',', '.', ';', ':', '?', '!']
    #text_c = nlp('start1 ' + 'start2 ' + text_clean + ' end')
    #text_p = nlp('start1 ' + 'start2 ' + text_punc + ' end')

    text_c = nlp(text_clean)
    text_p = nlp(text_punc)
    #corrections = []

    new_text = text_clean
    for i in range(2, len(text_p)):
        if text_p[i].text in punctuation:
            bigram = (text_p[i-2].text, text_p[i-1].text)
            index = find_bigram(bigram, text_c.text)
            #index = new_text.find(text_p[i-2].text +' ' + text_p[i-1].text)
            new_text = new_text.replace(text_c[index].text, text_c[index].text + text_p[i].text)
            #print(new_text)
            #corrections.append( (index, text_p[i].text) )
    return new_text

def execute(metadata_file):
    with open(metadata_file) as f:
        content_file = f.readlines()

    filepath = dirname(metadata_file)
    #output_file = open(join(args.base_dir,output_file), 'w')
    separator = '|'
 
    for line in content_file:

        filename, text_clean, text_punc, lev = line.split('|')
        folder1, folder2, _ = filename.split('_')
        filepath = join(filepath, folder1, folder2, filename + '.wav')

        new_text = correct_punctuation(text_clean, text_punc)
        print(text_clean)
        print(new_text)
        print(text_punc)
        line = separator.join([filepath, new_text.strip()])
        #print(line)
        #output_file.write(line + '\n')
    #output_file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input_dir', default='./input/train')
    parser.add_argument('--csv_file', default='output.txt', help='Name of csv file')
    parser.add_argument('--out_file', default='revised.csv', help='Name of csv result ile')      
    args = parser.parse_args()
    i = 0
    for metadata in glob.glob(join(args.base_dir, args.input_dir) + '/**/**/' + args.csv_file ):
        execute(metadata)
        if i==10:
            break
        i+=1
if __name__ == "__main__":
    main()
