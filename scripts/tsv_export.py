import pandas as pd
import copy
import os

# import custom-made functions
from time_format_converter import convert_time_float_to_string


### Create a function to adjust the timestamps of the last phoneme in each segment=========================================
def get_last_phoneme_timestamp(segment, word, puncts):
    #get the start and end time of the last phoneme
    if word.get("word").count(".") > 1: #the count is to ignore prolonged utterance like "ik..."
        last_phoneme_end = word.get("end")
    elif word.get("word")[-1] not in puncts: #if the last phoneme of the word is not a punctuation or in the word2vec dictionary, then this word isn't the last word in the segment
        last_phoneme_end = word.get("end")
    elif "è" in word.get("word"): #this is to handle the case where the last phoneme is è, which is not in the word2vec dictionary
        last_phoneme_end = word.get("end")
    elif word.get("word")[-1].isnumeric() or word.get("word")[-2].isnumeric(): #if the last or second-to-last character is a number, then set the end time to the end time of the word
        last_phoneme_end = word.get("end")
    else:
        try:
            index_word = segment["text"].index(word.get("word"))
            index_phoneme = index_word + len(word.get("word")) - 2
        except:
            print(f"ERROR: The word is not in the segment. Word = {word.get('word')}; Segment = {segment['text']}")
        
        try:
            last_phoneme_dict = segment["chars"][index_phoneme]
            last_phoneme_start = last_phoneme_dict["start"]
            last_phoneme_end_original = last_phoneme_dict["end"]
            duration = last_phoneme_end_original - last_phoneme_start
        except:
            print(f"ERROR: There is no phoneme in the segment. Phoneme = {last_phoneme_dict['char']}; Word = {word.get('word')}; Segment = {segment['text']}")
        
        #if the duration is longer than 1 second, we will set the end time to 50ms after the start time
        if duration > 1:
            last_phoneme_end = last_phoneme_start + 0.050 #if the duration is longer than 1 second, we will set the end time to 50ms after the start time
        else:
            last_phoneme_end = word.get("end") #if the duration is less than 1 second, we will set the end time to the end time of the word
    
    return convert_time_float_to_string(last_phoneme_end)



############# Define functions to export the transcript as a tsv file ##################

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


def format_transcript(result, filename, output_folder, puncts, word_spacing=True):
    #if word_spacing is True, we will add a space between words (some languages don't have spaces between words in the transcript)
    if word_spacing:
        word_space = " "
    else:
        word_space = ""

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
        n_words = len(segment["words"])

        for word in segment["words"]:
            #### First word (empty "text" variable) ####
            if text == "" or second_count == 1:
                text = word.get("word")
                segment["start_word"] = text
                segment["start_word_timestamp"] = convert_time_float_to_string(word.get("start"))               
                # "end_word" and "end_word_timestamp" will be overwritten if there are multiple words within one segment
                segment["end_word"] = text
                segment["end_word_timestamp"] = get_last_phoneme_timestamp(segment, word, puncts)
                if word.get("word")[-1] not in puncts:
                    previous_endTime = convert_time_float_to_string(word.get("end"))
                second_count = 0 #reset second_count so that next word won't be considerd as the start word

            #### Last word ####
            elif count == n_words-1: #if this is the last word
                text += word_space + word.get("word")
                if word.get("end") is not None:
                    segment["end_word"] = word.get("word")
                    segment["end_word_timestamp"] = get_last_phoneme_timestamp(segment, word, puncts)
                    previous_endTime = get_last_phoneme_timestamp(segment, word, puncts)
                else:
                    segment["end_word_timestamp"] = previous_endTime

            #### Middle words ####
            else:
                text += word_space + word.get("word")
                #### Words that end with punctuations ####
                # if the word contains a punctuation, we will make a row for this utterance
                if word.get("word")[-1] in puncts:
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

    output_filename = os.path.join(output_folder, "tsv", filename)

    return df_output, output_filename

def export_transcript_as_tsv(result, filename, output_folder, puncts):
    df_output, output_filename = format_transcript(result, filename, output_folder, puncts)
    # we only need the following columns
    df_output = df_output[['start_word_timestamp', 'end_word_timestamp', 'text_final']]
    #change column names
    df_output = df_output.rename(columns={"start_word_timestamp": "start", "end_word_timestamp": "end", "text_final": "text"})
    df_output.to_csv(output_filename, index=False, sep="\t")


def export_transcript_as_textonly(result, filename, output_folder):
    transcript = copy.deepcopy(result)
    # make an empty dataframe to store the output
    df_output = pd.DataFrame(columns=["text"])

    # save result["segments"] as segments so that I don't need to type result[""] everytime
    segments = transcript["segments"]

    #list all the keys to be removed from the output
    remove_keys = ["seek", "tokens"]
    for segment in segments:
        for key in remove_keys:
            if key in segment:
                del segment[key]

    for segment in segments:
        #make a row for each segment
        row = pd.DataFrame([segment], columns=["text"])
        df_output = pd.concat([df_output, row], ignore_index=True)

    output_filename = os.path.join(output_folder, "text_only", filename)
    df_output.to_csv(output_filename, header=None, index=False)