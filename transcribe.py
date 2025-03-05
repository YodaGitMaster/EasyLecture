import os
import argparse
import math
import logging
import torch
import time
from transformers import pipeline

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def split_chunk(chunk, max_duration=30.0):
    start, end = chunk.get("timestamp", (0.0, 0.0))
    duration = end - start
    text = chunk["text"]
    segments = math.ceil(duration / max_duration)
    segment_lines = []

    text_len = len(text)
    for i in range(segments):
        seg_start = start + i * max_duration
        seg_end = min(start + (i + 1) * max_duration, end)
        idx_start = int(round(i * text_len / segments))
        idx_end = int(round((i + 1) * text_len / segments))
        seg_text = text[idx_start:idx_end].strip()
        line = f"[{seg_start:.2f}-{seg_end:.2f}] {seg_text}"
        segment_lines.append(line)
    return segment_lines


def transcribe_audio(input_path, output_path, model_name="openai/whisper-medium.en", return_timestamps=False):
    try:
        script_dir = os.path.abspath(os.path.dirname(__file__))
        ffmpeg_bin = os.path.join(script_dir, "bin")
        os.environ["PATH"] = ffmpeg_bin + \
            os.pathsep + os.environ.get("PATH", "")

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {device}")

        pipe = pipeline("automatic-speech-recognition",
                        model=model_name, chunk_length_s=30, device=device)
        start_time = time.time()

        if return_timestamps:
            result = pipe(input_path, batch_size=8, return_timestamps=True)
            lines = []
            for chunk in result.get("chunks", []):
                start, end = chunk.get("timestamp", (0.0, 0.0))
                if start is None or end is None:
                    if start is None:
                        start = 0.0
                    if end is None:
                        end = start + 30.0
                if (end - start) > 30.0:
                    segment_lines = split_chunk(chunk, max_duration=30.0)
                    lines.extend(segment_lines)
                else:
                    line = f"[{start:.2f}-{end:.2f}] {chunk['text'].strip()}"
                    lines.append(line)
            transcription = "\n".join(lines)
        else:
            result = pipe(input_path, batch_size=8)
            transcription = result["text"]

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcription)

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Transcription saved to {output_path}")
        print(f"Transcription completed in {elapsed_time:.2f} seconds.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file using Whisper.")
    parser.add_argument("input", help="Path to the input audio file.")
    parser.add_argument("output", help="Path to the output text file.")
    parser.add_argument("--timestamps", action="store_true",
                        help="Include timestamps in the transcription output.")
    parser.add_argument("--model", default="openai/whisper-tiny.en",
                        help="Name of the model to use for transcription.")
    args = parser.parse_args()
    transcribe_audio(args.input, args.output,
                     model_name=args.model, return_timestamps=args.timestamps)

# Command List:
# Run basic transcription:
# python transcribe.py input_audio.wav output_text.txt
#
# Run transcription with timestamps:
# python transcribe.py input_audio.wav output_text.txt --timestamps
#
# Run transcription with a specific model:
# python transcribe.py input_audio.wav output_text.txt --model openai/whisper-large.en
#
# Run transcription with both timestamps and a specific model:
# python transcribe.py input_audio.wav output_text.txt --timestamps --model openai/whisper-base.en
