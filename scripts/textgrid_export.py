import tgt
import os
import copy

# import custom-made functions
from time_format_converter import convert_time_float_to_string, convert_string_to_float
from tsv_export import get_last_phoneme_timestamp


def get_tiers(result, sentence_tier, word_tier, puncts, word_spacing):
    #if word_spacing is True, we will add a space between words (some languages don't have spaces between words in the transcript)
    if word_spacing:
        word_space = " "
    else:
        word_space = ""

    transcript = copy.deepcopy(result)

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
                start_time = word.get("start")
                end_time = convert_string_to_float(get_last_phoneme_timestamp(segment, word, puncts))
                if word.get("word")[-1] not in puncts:
                    previous_endTime = end_time
                second_count = 0 #reset second_count so that next word won't be considerd as the start word

            #### Last word ####
            elif count == n_words-1: #if this is the last word
                text += word_space + word.get("word")
                if word.get("end") is not None:
                    end_time = convert_string_to_float(get_last_phoneme_timestamp(segment, word, puncts))
                    word["end"] = end_time
                    previous_endTime = end_time
                else:
                    segment["end_word_timestamp"] = previous_endTime

            #### Middle words ####
            else:
                text += word_space + word.get("word")
                #### Words that end with punctuations ####
                # if the word contains a punctuation, we will make a row for this utterance
                if word.get("word")[-1] in puncts:
                    end_time = convert_string_to_float(get_last_phoneme_timestamp(segment, word, puncts))
                    
                    ### make new interval for the sentence tier
                    interval = tgt.Interval(start_time=float(start_time), end_time=float(end_time), text=text)
                    sentence_tier.add_interval(interval)

                    second_count += 1
                    text = ""
                    continue #skip the rest of the loop and go to the next word
            
            try:
                interval = tgt.Interval(start_time=float(word["start"]), end_time=float(word["end"]), text=word["word"])
                word_tier.add_interval(interval)
            except:
                print("Error in word: ", word)
            count += 1

        if second_count == 0: #if the row for the utterance has not been made yet (because we didn't have to split the utterance)
            ### make new interval for the sentence tier
            interval = tgt.Interval(start_time=float(start_time), end_time=float(end_time), text=text)
            sentence_tier.add_interval(interval)  
        
    return sentence_tier, word_tier


def export_transcript_as_textgrid(result, filename, output_folder, puncts, word_spacing=True):
    tg = tgt.TextGrid()

    sentence_tier = tgt.IntervalTier(start_time=0, end_time=result["segments"][-1]["end"], name="sentence")
    word_tier = tgt.IntervalTier(start_time=0, end_time=result["segments"][-1]["end"], name="word")

    sentence_tier, word_tier = get_tiers(result, sentence_tier, word_tier, puncts, word_spacing)

    tg.add_tier(sentence_tier)
    tg.add_tier(word_tier)

    output_file_name = os.path.splitext(filename)[0] + ".TextGrid"
    output_path = os.path.join(os.path.dirname(output_folder), "textgrid", output_file_name)

    tgt.write_to_file(tg, output_path, format='short')
