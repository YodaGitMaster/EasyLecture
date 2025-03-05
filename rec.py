import time
import sys
import pyaudiowpatch as pyaudio
import numpy as np
import wave
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def list_loopback_devices(p):
    return list(p.get_loopback_device_info_generator())


def record_short_sample(p, device_index, duration=2):
    device_info = p.get_device_info_by_index(device_index)
    fs = int(device_info["defaultSampleRate"])
    channels = device_info["maxInputChannels"]
    frames_per_buffer = 1024
    audio_buffer = []

    def callback(in_data, frame_count, time_info, status):
        audio_buffer.append(in_data)
        return (in_data, pyaudio.paContinue)

    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=fs, input=True,
                    frames_per_buffer=frames_per_buffer, input_device_index=device_index, stream_callback=callback)
    stream.start_stream()
    time.sleep(duration)
    stream.stop_stream()
    stream.close()
    audio_bytes = b"".join(audio_buffer)
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
    if channels > 1:
        audio_np = audio_np.reshape(-1, channels)
        audio_np = np.mean(audio_np, axis=1)
    return audio_np, fs


def compute_rms(audio_np):
    return np.sqrt(np.mean(np.square(audio_np), dtype=np.float64))


def test_all_devices(duration=2, rms_threshold=500):
    p = pyaudio.PyAudio()
    devices = list_loopback_devices(p)
    active_devices = []
    logger.info("Testing loopback devices for audio activity...")
    for dev in devices:
        index = dev["index"]
        name = dev["name"]
        logger.info(f"Testing device [{index}] {name}")
        try:
            audio_np, fs = record_short_sample(p, index, duration)
            rms = compute_rms(audio_np)
            logger.info(f"Device [{index}] RMS: {rms:.2f}")
            if rms > rms_threshold:
                logger.info(f"--> Audio detected on device [{index}] {name}")
                active_devices.append((index, name, rms))
            else:
                logger.info(
                    f"--> No significant audio on device [{index}] {name}")
        except Exception as e:
            logger.error(f"Error testing device [{index}] {name}: {e}")
    p.terminate()
    return active_devices


def select_device_from_active(duration=2, rms_threshold=500):
    active_devices = test_all_devices(
        duration=duration, rms_threshold=rms_threshold)
    if not active_devices:
        logger.info("No devices with significant audio activity were detected.")
        prompt = input(
            "Do you want to list all available loopback devices and choose one anyway? (y/n): ").strip().lower()
        if prompt != "y":
            return None
        else:
            p = pyaudio.PyAudio()
            all_devices = list_loopback_devices(p)
            if not all_devices:
                logger.info("No loopback devices found.")
                p.terminate()
                return None
            logger.info("Available loopback devices:")
            for dev in all_devices:
                logger.info(f"Device [{dev['index']}] {dev['name']}")
            p.terminate()
            while True:
                selection = input(
                    "Enter the device index from the list above (or 'q' to quit): ").strip()
                if selection.lower() == "q":
                    return None
                try:
                    sel = int(selection)
                    if any(dev['index'] == sel for dev in all_devices):
                        logger.info(f"You selected device [{sel}].")
                        return sel
                    else:
                        logger.info("Invalid device index. Please try again.")
                except ValueError:
                    logger.info(
                        "Invalid input. Please enter a numeric device index.")
    else:
        logger.info("Devices with audio activity:")
        for device_index, name, rms in active_devices:
            logger.info(f"Device [{device_index}] {name} (RMS: {rms:.2f})")
        while True:
            selection = input(
                "Enter the device index from the list above (or 'q' to quit): ").strip()
            if selection.lower() == 'q':
                return None
            try:
                sel = int(selection)
                if any(dev[0] == sel for dev in active_devices):
                    logger.info(f"You selected device [{sel}].")
                    return sel
                else:
                    logger.info(
                        "Invalid device index. Please enter one of the indices shown above.")
            except ValueError:
                logger.info(
                    "Invalid input. Please enter a numeric device index.")


def record_audio(output_file, device_index, silence_threshold=500, silence_timeout=30):
    p = pyaudio.PyAudio()
    logger.info(f"Using WASAPI loopback device index: {device_index}")
    device_info = p.get_device_info_by_index(device_index)
    fs = int(device_info["defaultSampleRate"])
    channels = device_info["maxInputChannels"]
    logger.info(f"Recording at {fs} Hz, {channels} channel(s)")
    audio_buffer = []
    last_sound_time = time.time()

    def callback(in_data, frame_count, time_info, status):
        nonlocal last_sound_time
        audio_buffer.append(in_data)
        chunk = np.frombuffer(in_data, dtype=np.int16)
        if channels > 1:
            chunk = chunk.reshape(-1, channels)
            chunk = np.mean(chunk, axis=1)
        rms = np.sqrt(np.mean(np.square(chunk), dtype=np.float64))
        if rms > silence_threshold:
            last_sound_time = time.time()
        return (in_data, pyaudio.paContinue)

    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=fs, input=True,
                    frames_per_buffer=1024, input_device_index=device_index, stream_callback=callback)
    stream.start_stream()
    logger.info(
        "Recording desktop audio. Press Ctrl+C to stop, or it will auto-stop after " f"{silence_timeout} seconds of silence.")
    try:
        while stream.is_active():
            time.sleep(0.1)
            if time.time() - last_sound_time > silence_timeout:
                logger.info(
                    "No significant audio detected for the timeout period. Stopping recording automatically.")
                break
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping recording...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    audio_data = b"".join(audio_buffer)
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(audio_data)
    wf.close()
    logger.info(f"Audio recording saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            chosen_index = int(sys.argv[1])
            logger.info(f"Using provided device index: {chosen_index}")
        except ValueError:
            logger.error(
                "Invalid command-line argument. Expected an integer device index.")
            sys.exit(1)
    else:
        chosen_index = select_device_from_active(duration=2, rms_threshold=500)
        if chosen_index is None:
            logger.info("No device selected. Exiting.")
            sys.exit(0)
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        logger.info(f"Using provided output file name: {output_file}")
    else:
        output_file = "output_audio.wav"
    logger.info(f"Selected device index: {chosen_index}")
    record_audio(output_file, device_index=chosen_index,
                 silence_threshold=500, silence_timeout=30)

# Command-line options:
# 1. python rec.py <device_index> <output_file>
#    - Example: python rec.py 32 my_recording.wav
# 2. python rec.py <device_index>
#    - Example: python rec.py 32
# 3. python rec.py
#    - Example: python rec.py
