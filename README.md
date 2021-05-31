# Multilingual LibriSpeech (MLS) Dataset Conversion Tools 

Set of tools to convert the MLS dataset. 

## Install

Create a conda env:
```
$ conda create -n mls_converter python=3.8 pip
$ conda activate mls_converter
```


```
sudo apt-get update
sudo apt-get install ffmpeg

```
Next, install the mls_converter requirements:

```
$ pip install -r requirements.txt
```

For an specific language, install Spacy:

```
# Portuguese
$ python3 -m spacy download pt_core_news_md
# Polish
$ python3 -m spacy download pl_core_news_sm
# Italian
$ python3 -m spacy download it_core_news_sm
# Spanish
$ python3 -m spacy download es_core_news_sm
# French
$ python3 -m spacy download fr_core_news_sm
# Dutch
$ python3 -m spacy download nl_core_news_sm
# German
$ python3 -m spacy download de_core_news_sm
# English
$ python3 -m spacy download en_core_web_sm
```

## Audio Converter

This script downloads the original audio files directly from librivox and converts them to a better quality sample rate (22kHz as default). It is necessary to define the language, which will be downloaded, and extract the files needed to download each file separately.

```
python3 execute_audio_converter.py --language=pt --sampling_rate=22050 --audio_format=wav
```

## Text Converter

Given a file of transcripts (without punctuation) and a file containing the texts of the books with punctuation (but with errors), this script adds punctuation in the transcripts. 

To do this, perform a search for each sentence in the text of the books. As the texts are long and are not necessarily in sequence, this script creates threads, which divide the text from the books and search separately for the corresponding sentence.

```
python3 execute_text_converter_on_folder.py --base_dir=./ --metric=hamming --input_folder=./input/train --books_folder=./lv_text/portuguese/ --number_threads=10 --search_type=word
```