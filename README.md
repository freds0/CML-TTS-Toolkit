# CML-TTS Rebuild Tools 

This repository allows you to reconstruct the CML-TTS dataset from segment files. To do this, you must download the txt files containing the segments, which are available at [Google Drive](https://drive.google.com/file/d/102DxVPyR9VgRFIZaFtEHJ3u_YAW9ZnEq/view?usp=sharing) and [One Drive](https://ufmtbr-my.sharepoint.com/:u:/g/personal/fredoliveira_ufmt_br/EScW5_fYuvtIslONTsyYJhsBiu8nzWwjDRFmMc8qBrpa7g?e=Ebrnrh).

## Rebuild CML-TTS Dataset

To recreate the CML-TTS Dataset, you need to execute the following command:
```
python3 recreate_cml_dataset.py \
    --input_segments=FILEPATH.txt \
    --sampling_rate=SR \
    --output_dir=OUTPUT_DIRECTORY \
    --audio_format=AUDIO_FORMAT \ 
    --audio_quality=MP3_QUALITY
```

Where:
- FILEPATH.txt  indicates the filepath of the file containing the segments of a specific set (train, test, or dev).
- SR indicates the sampling rate of the files (22050 or 44100).
- OUTPUT_DIRECTORY is the directory where the CML-TTS Dataset will be reconstructed.
- AUDIO_FORMAT is the format of the files (wav or flac).
- MP3_QUALITY indicates the quality of the mp3 files to be downloaded (set to 64 if sampling_rate=22050, or 128 if sampling_rate=44100).


For example, to reconstruct the 'train' set of the CML-TTS Dataset in Portuguese, the command should be as follows:

```
python3 recreate_cml_dataset.py \
    --input_segments=cml_train_segments_pt.txt \
    --sampling_rate=22050 \
    --output_dir=mls_portuguese_opus/train/audio \
    --audio_format=wav \ 
    --audio_quality=64
```


## Create CML-TTS Dataset Segments

If for some reason you are unable (or unwilling) to use the CML-TTS dataset segments, and want to recreate them, you can use the following script, which uses the CML-TTS Dataset files and the MLS dataset segments:


```
python3 create_segment_file.py \
    --cml_csv=FILEPATH.txt \
    --cml_dir=DATASET_DIR \
    --mls_csv=MLS_SEGMENTS_FILEPATH.csv \
    --output_csv=OUTPUT_CML_SEGMENTS_FILEPATH.txt
```

Where:
- FILEPATH.txt  indicates the filepath of the file containing the segments of a specific set (train, test, or dev), where each line contains: "wav_filename,wav_filesize,transcript,transcript_wav2vec,levenshtein,duration,num_words,client_id".
- DATASET_DIR is the directory where is the CML-TTS Dataset.
- MLS_SEGMENTS_FILEPATH is the MLS Dataset segments csv file.
- OUTPUT_CML_SEGMENTS_FILEPATH is the filepath of the output file containing the CML segments.
