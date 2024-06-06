from moviepy.editor import VideoFileClip
import os

# Create a function to convert video to mp4======================================
def extract_wav(path):
    wav_file = path[:-4] + ".wav"
    #if the filename ends with .mov AND the same filename with .wav doesn't exist
    if (path.endswith(".mov") or path.endswith(".mp4")) and not os.path.exists(wav_file):
        print(f"Extracting audio from {path}")
        file = path

        ### extract audio from the video
        # Load the video clip
        video_clip = VideoFileClip(file)
        # Extract the audio from the video clip
        audio_clip = video_clip.audio
        # Write the audio to a separate file
        audio_clip.write_audiofile(wav_file)

        # Close the video and audio clips
        audio_clip.close()
        video_clip.close()