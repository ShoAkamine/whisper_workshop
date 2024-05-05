import pandas as pd
import copy
import os

# import custom-made functions
from time_format_converter import convert_time_float_to_string


### Define functions to export the transcript as a tsv file ###

def make_row_for_each_segment(segment, text, df_output):
    #make a row for each segment
    row = pd.DataFrame([segment], columns=["start_word_timestamp", "end_word_timestamp", "text_final", 
                                           "start_word", "end_word", "start", "end", "text",
                                           "temperature", "avg_logprob", "compression_ratio", 
                                           "no_speech_prob", "confidence"])
    #make a new column "text"
    row["text_final"] = text
    # append the row to the output dataframe using concat
    df_output = pd.concat([df_output, row], ignore_index=True)
    return df_output


def format_transcript(result, filename, output_folder):
    transcript = copy.deepcopy(result)
    # make an empty dataframe to store the output
    df_output = pd.DataFrame(columns=["start_word_timestamp", "end_word_timestamp", "text_final", 
                                      "start_word", "end_word", "start", "end", "text",
                                      "temperature", "avg_logprob", "compression_ratio", 
                                      "no_speech_prob", "confidence"])

    # save result["segments"] as segments so that I don't need to type result[""] everytime
    segments = transcript["segments"]

    #list all the keys to be removed from the output
    remove_keys = ["seek", "tokens"]
    for segment in segments:
        for key in remove_keys:
            if key in segment:
                del segment[key]

    #extract timestamps for the first word and the last word from whole_word_timestamps
    #also append words to form an utterance
    for segment in segments:
        text = ""
        count = 0
        second_count = 0 #this is for the case where there are multiple sentences within one segment
        first_word_disfluency = False

        for word in segment["words"]:
            if word.get("word") == "[*]":
                if count == 0:
                    first_word_disfluency = True
                count += 1
                continue #go to the next word
            
            elif count == 0 or second_count == 1 or first_word_disfluency: #if this is the first word and not a disfluency marker
                text = word.get("word")
                segment["start_word"] = text
                segment["start_word_timestamp"] = convert_time_float_to_string(word.get("start"))               
                # "end_word" and "end_word_timestamp" will be overwritten if there are multiple words within one segment
                segment["end_word"] = text
                segment["end_word_timestamp"] = convert_time_float_to_string(word.get("end"))
                second_count = 0 #reset second_count so that next word won't be considerd as the start word
                first_word_disfluency = False

            elif count == len(segment["words"]) -1: #if this is the last word
                text += " " + word.get("word")
                segment["end_word"] = word.get("word")
                segment["end_word_timestamp"] = convert_time_float_to_string(word.get("end"))

            else:
                text += " " + word.get("word")
                # if the word contains a punctuation and not the last word in the segment, we will make a row for this utterance
                if word.get("word")[-1] in [".", "?", "!"]:
                    segment["end_word"] = word.get("word")
                    segment["end_word_timestamp"] = convert_time_float_to_string(word.get("end"))
                    
                    df_output = make_row_for_each_segment(segment, text, df_output)
                    second_count += 1
                    text = ""
                    continue #skip the rest of the loop and go to the next word
            
            count += 1
        if second_count == 0: #if the row for the utterance has not been made yet (because we didn't have to split the utterance)
            df_output = make_row_for_each_segment(segment, text, df_output)    
            

    #before exporint the dataframe, we will format start and end timestamps & 
    #fill empty timestamps for one-word utterance because such utterances do not have end words/timestamps
    for index, row in df_output.iterrows():
        df_output.loc[index, 'start'] = convert_time_float_to_string(df_output.loc[index, 'start'])
        df_output.loc[index, 'end'] = convert_time_float_to_string(df_output.loc[index, 'end'])
        
        # if pd.isnull(df_output.loc[index, "end_word_timestamp"]):
        #     df_output.loc[index, 'end_word_timestamp'] = df_output.loc[index, "end"]

    output_filename_pair = filename.split("_denoised")[0]
    output_filename_pair = output_filename_pair.split(".txt")[0]
    output_filename = os.path.join(output_folder, "tsv", output_filename_pair)

    return df_output, output_filename

def export_transcript_as_tsv(result, filename, output_folder):
    df_output, output_filename = format_transcript(result, filename, output_folder)
    # we only need the following columns
    df_output = df_output[['start_word_timestamp', 'end_word_timestamp', 'text_final']]
    #change column names
    df_output = df_output.rename(columns={"start_word_timestamp": "start", "end_word_timestamp": "end", "text_final": "text"})
    df_output.to_csv(f"{output_filename}.txt", index=False, sep="\t")


def export_transcript_as_tsv_textonly(result, filename, output_folder):
    df_output, output_filename = format_transcript(result, filename, output_folder)
    # we only need the text_final column
    df_output = df_output[['text_final']]
    # remove the column header so that the output starts with the first row
    df_output = df_output.rename(columns={'text_final': ''})
    df_output.to_csv(f"{output_filename}.txt", index=False, sep="\t")