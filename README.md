# WhisperX tutorial for language sciences
This tutorial aims to help students and researchers in language sciences transcribe speech automatically using WhisperX---the state-of-the-art automatic speech recognition pipeline based on OpenAI's Whisper. I take the following approach:

1. Run WhisperX to get time-aligned transcript
2. Export it as the following file formats:
    - Praat TextGrid file
    - Tab-separated text file (with timestamps)
    - text file (without timestamps), which can be submitted to [WebMAUS](https://clarin.phonetik.uni-muenchen.de/BASWebServices/interface/WebMAUSBasic) together with wav files for phoneme-level and more accurate timestamps. 
    - SRT file for subtitles


## Requirements
Before running the script, you need to have the following installed:
- [Anaconda](https://www.anaconda.com/download/success)
- [Visual Studio Code](https://code.visualstudio.com/download) (or an IDE of your preference).


## Instructions
You can run WhisperX and export the trascript by following the steps below:

1. Download the repository. You can do so in two different ways:

    Option 1: clone the repository \\
    Option 2: click the green "<> Code" button on this page and select "Download ZIP". Make sure to unzip the folder before moving on to the next step. 

2. Go to the "scripts" folder

3. Open the "whisper.ipynb" file in Visual Studio Code

4. Set up the conda environment by following the instructions under the "Install packages" section.

5. Run the script


## Error solution guide
If you encounter some issues running the whisper.ipynb notebook, please check [this document](https://docs.google.com/document/d/1GwX3aM83n4W-JVmOpEvhqh_H0Fmwd2kcZDsic5WiXR4/edit?usp=sharing) for solutions! 

