# YouTube Channel Audio Downloader and Multi-Language Transcriber

This Streamlit application downloads audio from all videos on a specific YouTube channel (provided as a handle or URL) and transcribes them in one of several Indian languages using [OpenAI Whisper](https://github.com/openai/whisper). The transcriptions are saved in both CSV and a multi-sheet Excel file for easy reference.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Arguments and Interface](#arguments-and-interface)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

1. **YouTube Handle/URL Parsing**  
   Enter a YouTube handle (e.g., `@SangamTalks`) or URL (`https://www.youtube.com/@SangamTalks`), and the script will automatically derive the channel’s ID using the [YouTube Data API](https://developers.google.com/youtube/v3).

2. **Multiple Language Support**  
   The script supports transcribing audio in various Indian languages (e.g., Kannada, Hindi, Tamil, Marathi, Gujarati, Punjabi, Bengali), by mapping the human-readable language name to its Whisper-compatible code.

3. **Audio Download**  
   Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download the audio in MP3 format from YouTube videos (one channel at a time).

4. **Transcription**  
   Uses [OpenAI Whisper](https://github.com/openai/whisper) for automatic speech recognition (ASR). It supports the `base`, `small`, `medium`, `large` models, but the code is currently set up to use `turbo` (a locally installed model name; you can adjust as needed).

5. **Result Packaging**  
   - Generates a **CSV** transcription file per video.
   - Optionally creates a **single multi-sheet Excel file** (XLSX) containing transcripts for all videos in one place.

6. **Resumable**  
   - If a video’s audio is already downloaded, it won’t download again.
   - If a transcription CSV already exists for a video, it won’t transcribe again (useful for large batches).

---

## Tech Stack

- [Streamlit](https://streamlit.io/) — For the web interface.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — For downloading audio from YouTube.
- [Whisper](https://github.com/openai/whisper) — For speech-to-text transcription.
- [pandas](https://pandas.pydata.org/) — For data handling, CSV reading/writing, and Excel exports.
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/) — For creating multi-sheet Excel files.
- [google-api-python-client](https://github.com/googleapis/google-api-python-client) — For making calls to the YouTube Data API.

---

## Installation

1. **Clone the repository** (or copy the code files):
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. **Create a virtual environment (recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate    # On macOS/Linux
    # Or venv\Scripts\activate  # On Windows
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    Where `requirements.txt` might include:
    ```txt
    streamlit
    yt-dlp
    openai-whisper
    google-api-python-client
    openpyxl
    pandas
    ```
    (Adjust your `requirements.txt` to match exactly the libraries/versions you need.)

4. **Obtain a YouTube Data API key** from [Google Cloud Console](https://console.cloud.google.com/).  
   - Create a project, enable the YouTube Data API v3, and create an API key.
   - Copy the key for use in the application.

---

## Usage

1. **Run the Streamlit app**:
    ```bash
    streamlit run your_script.py
    ```
   Replace `your_script.py` with the filename containing the provided code (if it’s something else).

2. **Open your browser**  
   After starting Streamlit, it will usually open `http://localhost:8501` automatically. If not, open that URL manually.

---

## Arguments and Interface

The Streamlit interface provides:

1. **YouTube Channel Handle/URL**  
   - Examples: `@SangamTalks`, `https://www.youtube.com/@SangamTalks`.  
   - **Note**: Must begin with an `@` if typed directly or must be a valid YouTube channel URL.

2. **YouTube Data API Key**  
   - Paste your API key to authenticate queries to the YouTube Data API.

3. **Select Transcription Language**  
   - A dropdown menu with supported Indian languages (Kannada, Hindi, Tamil, Marathi, Gujarati, Punjabi, Bengali).

4. **Process Channel**  
   - Clicking this button initiates:
     - Resolving the channel ID via the handle/URL.
     - Fetching **all** video IDs from the channel.
     - For each video:
       - Downloading the audio if not already present.
       - Transcribing if a CSV for that video doesn’t already exist.

---

## Output Files

1. **Audio Files**  
   - Located in the folder `./audio_files`.  
   - Each file is named as `<video_id>.mp3`.

2. **Per-Video CSV**  
   - Also stored in `./audio_files`.  
   - Each file is named as `<video_id>_transcription.csv`.
   - Contains columns for: `["Video ID", "Start Time (s)", "End Time (s)", "Transcript"]`.

3. **Multi-Sheet Excel**  
   - Once all videos are processed, the script compiles all transcripts into a single Excel file located at `./audio_files/all_transcripts_multisheet.xlsx`.
   - Each video’s transcript is in a separate worksheet named after the video ID (truncated to 31 chars if needed).

---

## Troubleshooting

1. **Invalid YouTube Handle**  
   - Make sure your handle is in the format `@channelName` or you have a valid URL like `https://www.youtube.com/@channelName`.

2. **Missing or Invalid YouTube Data API Key**  
   - Ensure the key is valid and you have enabled the YouTube Data API in your Google Cloud project.

3. **Large Channels**  
   - For channels with hundreds or thousands of videos, note that the process might be slow. You can stop and re-run any time. Already-downloaded audio files and transcripts won’t be redone.

4. **Memory or Disk Space**  
   - Whisper transcription, especially if you use large models, can be memory-intensive.  
   - Ensure you have sufficient disk space for audio files and the final Excel file.

5. **Model Choice**  
   - The sample code uses `whisper.load_model("turbo")`. If you face issues with model names, replace `"turbo"` with `"small"`, `"medium"`, `"large"`, or any other locally available model.  

---

## License

This project is distributed under the [MIT License](LICENSE.md). Feel free to modify and use as per your needs.

---

**Enjoy the streamlined process of downloading and transcribing audio from entire YouTube channels!** If you have any issues, please open an issue or contribute a pull request.
