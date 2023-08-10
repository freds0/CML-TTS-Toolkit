import argparse
from os.path import join, dirname, basename, splitext
from tqdm import tqdm
import torchaudio

segments_dict = {}
data_segments_dict = None

def get_segment_duration(filepath):
    waveform, sample_rate = torchaudio.load(filepath)
    # Calcule a duração do segmento em milissegundos
    waveform = waveform.squeeze()
    segment_duration = float(len(waveform))/ (sample_rate)
    return segment_duration


def create_data_segments_dict(mls_segments_filepath):
    
    global data_segments_dict 
    data_segments_dict = {}

    with open(mls_segments_filepath) as f :
        segments_links = f.readlines()

    for line in segments_links:
        filename, link, begin, end = line.strip().split("\t")   
        data_segments_dict[filename] = (link, begin, end)    


def get_segmented_files(segments_filepath, cml_dir, mls_segments_filepath, output_filepath):

    global data_segments_dict
    content_data = ""
    with open(segments_filepath) as f :
        content_data = f.readlines()[1:]

    create_data_segments_dict(mls_segments_filepath)

    out_file = open(output_filepath, "w")

    for line in tqdm(content_data):
        #wav_filename,wav_filesize,transcript,transcript_wav2vec,levenshtein,duration,num_words,client_id = line.strip().split("|")
        wav_filename,_,_,_,_,_,_,_ = line.strip().split("|")
        
        # Get files path
        folder1, folder2, fileid = wav_filename.split('_')

        separator = "\t"
        if wav_filename.count("-") == 0: # file is not segmented
            filename = splitext(basename(wav_filename))[0]
            link, begin, end = data_segments_dict.get(filename, None)
            line = separator.join([filename, link, str(begin), str(end)])
            out_file.write(line + "\n")

        else: # file is segmented
            filename = basename(wav_filename)
            filename, seg_id = filename.split("-")

            data = data_segments_dict.get(filename, None)            
            if data is None:
                continue
            else:
                link, begin, end = data
            filepath = join(cml_dir, wav_filename)
            segment_duration = get_segment_duration(filepath)

            seg_id = seg_id.replace(".wav", "")
            if int(seg_id) == 1:
                begin = float(begin)
            else:
                previous_fileid = "{}-{:04d}".format(filename, int(seg_id) - 1)
                if previous_fileid in segments_dict:
                    begin = segments_dict[previous_fileid]
                else: 
                    print("Error: segment {} not found".format(previous_fileid))
                    continue

            end = begin + segment_duration

            fileid = "{}-{:04d}".format(filename, int(seg_id))
            segments_dict[fileid] = end
            line = separator.join([fileid, link, str(begin), str(end)])
            out_file.write(line + "\n")
        
    out_file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--cml_csv', default="train.csv")
    parser.add_argument('-d', '--cml_dir', default="cml_tts_dataset_portuguese_v0.1")
    parser.add_argument('-m', '--mls_csv', default="segments.csv")
    parser.add_argument('-o', '--output_csv', default="cml_train_segments.txt")
    args = parser.parse_args()

    get_segmented_files(args.cml_csv, args.cml_dir, args.mls_csv, args.output_csv)


if __name__ == "__main__":
    main()

