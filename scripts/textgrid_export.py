import tgt
import os

def export_transcript_as_textgrid(result, filename, output_folder):
    tg = tgt.TextGrid()

    sentences_tier = tgt.IntervalTier(start_time=0, end_time=result["segments"][-1]["end"], name="sentence")
    word_tier = tgt.IntervalTier(start_time=0, end_time=result["segments"][-1]["end"], name="word")
    phoneme_tier = tgt.IntervalTier(start_time=0, end_time=result["segments"][-1]["end"], name="phoneme")

    punctuations = [".", ",", "!", "?", " "]

    #work on words before it's too late
    for segment in result["segments"]:
        interval = tgt.Interval(start_time=float(segment["start"]), end_time=float(segment["end"]), text=segment["text"])
        sentences_tier.add_interval(interval)

        if "words" in segment:
            for word in segment["words"]:
                try:
                    interval = tgt.Interval(start_time=float(word["start"]), end_time=float(word["end"]), text=word["word"])
                    word_tier.add_interval(interval)
                except:
                    print("Error in word: ", word)

        if "chars" in segment:
            for phoneme in segment["chars"]:
                if phoneme["char"] in punctuations: #skip punctuations
                    continue
                try:
                    interval = tgt.Interval(start_time=float(phoneme["start"]), end_time=float(phoneme["end"]), text=phoneme["char"])
                    phoneme_tier.add_interval(interval)
                except:
                    print("Error in phoneme: ", phoneme)


    tg.add_tier(sentences_tier)
    tg.add_tier(word_tier)
    tg.add_tier(phoneme_tier)

    output_file_name = os.path.splitext(filename)[0] + ".TextGrid"
    output_path = os.path.join(os.path.dirname(output_folder), "textgrid", output_file_name)

    tgt.write_to_file(tg, output_path, format='short')
