import os
import pandas as pd

def export_transcript_as_srt(output_filename, tsv_folder, srt_folder):
    srt_file = os.path.join(srt_folder, f"{output_filename[:-4]}.srt")
    # Remove the file if it already exists to avoid appending to the file
    if os.path.exists(srt_file):
        os.remove(srt_file)

    df_transcript = pd.read_csv(os.path.join(tsv_folder, output_filename), sep="\t")

    segmentId = 0
    for index, row in df_transcript.iterrows():
        segmentId += 1
        segment = f"{segmentId}\n{row['start']} --> {row['end']}\n{row['text']}\n\n"
        with open(srt_file, "a", encoding="utf-8") as srtFile:
            srtFile.write(segment)
            