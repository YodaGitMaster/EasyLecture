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

**Run without arguments (automatic device selection):**

```sh
python rec.py
```

## Script Details

### Functions
- **list_loopback_devices(p):** Lists all available loopback devices.
- **record_short_sample(p, device_index, duration=2):** Records a short audio sample from the specified device.
- **compute_rms(audio_np):** Computes the Root Mean Square (RMS) value of the audio sample.
- **test_all_devices(duration=2, rms_threshold=500):** Tests all loopback devices for audio activity and returns a list of active devices.
- **select_device_from_active(duration=2, rms_threshold=500):** Allows the user to select a device from the list of active devices.
- **record_audio(output_file, device_index, silence_threshold=500, silence_timeout=30):** Records audio from the specified device and saves it to a WAV file.

### Logging
The script uses the logging library to provide informational and error messages. The log format includes the timestamp, log level, and message.

### Main Execution
- If a device index is provided as a command-line argument, the script uses that device.
- If no device index is provided, the script automatically tests all devices for audio activity and prompts the user to select a device.
- The recorded audio is saved to the specified output file or defaults to `output_audio.wav`.

## Example

To record audio from device index 32 and save it to `my_recording.wav`, run:

```sh
python rec.py 32 my_recording.wav
```

To automatically select a device and save the recording to the default file, run:

```sh
python rec.py
```

## Notes
- The script uses a silence threshold and timeout to automatically stop recording if no significant audio is detected for a specified period.
- Ensure that the `pyaudiowpatch` library is correctly installed and configured for your system.
