# CML-TTS Rebuild Tools 

This repository allows you to reconstruct the CML-TTS dataset from segment files. To do this, you must download the txt files containing the segments, which are available at https://github.com/freds0/CML-TTS-Dataset.

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
