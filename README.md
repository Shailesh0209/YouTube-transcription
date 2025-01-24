# YouTube Channel Audio Downloader & Multi-Language Transcriber

A Streamlit application that downloads audio from all videos in a specified YouTube channel (via handle or URL) and transcribes them using [OpenAI Whisper](https://github.com/openai/whisper). This tool supports multiple Indian languages and outputs the transcription (with timestamps) to CSV.

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Usage](#usage)  
5. [Configuration & How It Works](#configuration--how-it-works)  
6. [Limitations & Tips](#limitations--tips)  
7. [Contributing](#contributing)  
8. [License](#license)

---

## Features

- **Handle/URL-based Channel Detection**: Accepts a YouTube channel handle like `@SangamTalks` or a URL like `https://www.youtube.com/@SangamTalks`.  
- **Automatic Channel ID Resolution**: Converts the provided handle or URL into a channel ID for the YouTube Data API.  
- **Batch Download of All Videos**: Iterates through the entire channel, downloading audio tracks using [yt-dlp](https://github.com/yt-dlp/yt-dlp).  
- **Transcription with Whisper**: Uses the "large" Whisper model by OpenAI to transcribe audio in one of the following languages:
  - Kannada (`kn`)
  - Hindi (`hi`)
  - Tamil (`ta`)
  - Marathi (`mr`)
  - Gujarati (`gu`)
  - Punjabi (`pa`)
  - Bengali (`bn`)
- **Timestamped CSV Output**: Saves transcription segments (with start/end times) to CSV and provides a **Streamlit download button** for each file.

---

## Prerequisites

1. **Python 3.7+** (3.8 or higher recommended)  
2. **Pip** for installing dependencies  
3. **YouTube Data API Key**  
   - Sign up at [Google Cloud Console](https://console.cloud.google.com/), enable the **YouTube Data API v3**, then retrieve your API key.  
4. **FFmpeg**  
   - Required by `yt-dlp` and Whisper for audio extraction and processing.  
   - Install via your package manager (e.g., `brew install ffmpeg` on macOS, `sudo apt-get install ffmpeg` on Ubuntu), or download from [FFmpeg.org](https://ffmpeg.org/).

---

## Installation

1. **Clone** or **download** this repository:
   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo
   ```

2. **Create & Activate** a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install** required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   > Example `requirements.txt` might include:
   > ```
   > streamlit
   > yt-dlp
   > openai-whisper
   > google-api-python-client
   > ffmpeg-python
   > ```
   Adjust as needed.

---

## Usage

1. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```
2. **Open** the URL displayed in your terminal (e.g., `http://localhost:8501`) in your web browser.
3. **Enter** the required information in the interface:
   - **Channel Handle/URL**: Something like `@SangamTalks` or `https://www.youtube.com/@SangamTalks`.  
   - **YouTube Data API Key**: Paste your API key here.  
   - **Select Language** for transcription: One of the supported languages (Kannada, Hindi, Tamil, Marathi, Gujarati, Punjabi, Bengali).  
   - **Process Channel**: Click the **Process Channel** button.
4. **Wait** as the app:
   - Resolves the handle/URL to get the channel ID.  
   - Retrieves all video IDs in the channel.  
   - Downloads audio for each video via `yt-dlp`.  
   - Transcribes the audio using the Whisper "large" model.  
   - Saves transcripts (with timestamps) to CSV.  
   - Displays a **download button** to retrieve each CSV file.

---

## Configuration & How It Works

### 1. Channel Handle to Channel ID
- The app uses the YouTube Data API (search endpoint) to find the channel ID matching the given handle or URL path (e.g. `@SangamTalks`).  

### 2. Fetching All Videos
- A loop calls `youtube.search().list()` with `channelId`, retrieving up to 50 videos per page until no more pages remain.  

### 3. Downloading Audio
- For each video ID, `yt-dlp` downloads the **best audio** as an MP3 file.

### 4. Transcribing with Whisper
- The app loads OpenAI’s Whisper model in “large” mode (can be changed to smaller models if you prefer).  
- Depending on the selected language code (e.g. "ta" for Tamil), Whisper will transcribe.  

### 5. Output to CSV
- Each transcription is saved in a CSV file named `{video_id}_transcription.csv` under the `audio_files` folder.  
- CSV includes columns: Video ID, Start Time (s), End Time (s), and Transcript.  

---

## Limitations & Tips

1. **API Quota**: Fetching all videos from a large channel consumes more YouTube Data API quota. Watch your limits.  
2. **Time & Storage**:
   - Downloading + transcribing many videos can take considerable time and disk space, especially using the "large" Whisper model. Consider smaller models if you need faster processing.  
   - This is especially true for lengthy channels, so plan accordingly.  
3. **Languages**: The current code supports only certain Indic languages. You can easily add more languages by updating the mapping in `get_language_code()`.  
4. **FFmpeg Installation**: Ensure FFmpeg is installed and available in your PATH, otherwise `yt-dlp` or Whisper might fail.  
5. **Local vs Remote Deployment**: If you deploy on a remote server (e.g., Streamlit Cloud, Heroku), be mindful of memory and CPU constraints.  

---

## Contributing

We’d love your help! Please submit bug reports and pull requests via [GitHub Issues](https://github.com/yourusername/yourrepo/issues). Make sure to run tests and follow our code style guidelines before submitting changes.

---

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

---

**Happy Transcribing!** 

If you have any questions or issues, please [open a GitHub issue](https://github.com/yourusername/yourrepo/issues) or reach out to the repository maintainers.  
