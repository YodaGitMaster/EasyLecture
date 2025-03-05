# Audio Recording Script README

## Overview
This script is designed to record audio from loopback devices using the `pyaudiowpatch` library. It includes functionalities to list available loopback devices, test them for audio activity, and record audio to a WAV file. The script supports both automatic device selection based on audio activity and manual selection via command-line arguments.

## Requirements
- Python 3.x
- `pyaudiowpatch` library
- `numpy` library
- `wave` library (included in Python standard library)
- `logging` library (included in Python standard library)

## Installation
To install the required libraries, you can use pip:
```sh
pip install pyaudiowpatch numpy
```

Usage

The script can be run from the command line with various options:

**Run without arguments (automatic device selection):**

```sh
python rec.py
```

**Specify both device index and output file:**

```sh
python rec.py <device_index> <output_file>
```

_Example:_

```sh
python rec.py 32 my_recording.wav
```

**Specify only the device index:**

```sh
python rec.py <device_index>
```

_Example:_

```sh
python rec.py 32
```


## Notes
- The script uses a silence threshold and timeout to automatically stop recording if no significant audio is detected for a specified period.
- Ensure that the `pyaudiowpatch` library is correctly installed and configured for your system.



# Transcribe

## Install FFmpeg

FFmpeg is required for audio processing. Below are installation steps for different operating systems.

### Linux (Ubuntu/Debian)
```
sudo apt update
sudo apt install -y ffmpeg
```
### For Arch Linux:
```
sudo pacman -S ffmpeg
```

### Mac (Homebrew)
```
brew install ffmpeg
```
### Windows
```
    Download the latest FFmpeg release from ffmpeg.org.
    Extract the archive to a preferred location (e.g., C:\ffmpeg).
    Add FFmpeg to the system PATH:
        Open System Properties → Environment Variables.
        Under System Variables, find and edit Path.
        Add the path to FFmpeg’s bin directory (C:\ffmpeg\bin).
    Verify installation:

    ffmpeg -version
```


## Command List:
### Run basic transcription:
```python
python transcribe.py input_audio.wav output_text.txt
```
### Run transcription with timestamps:
```python
python transcribe.py input_audio.wav output_text.txt --timestamps
```
#
### Run transcription with a specific model:
```python
python transcribe.py input_audio.wav output_text.txt --model openai/whisper-large.en
```
### Run transcription with both timestamps and a specific model:
```python

python transcribe.py input_audio.wav output_text.txt --timestamps --model openai/whisper-base.en
```