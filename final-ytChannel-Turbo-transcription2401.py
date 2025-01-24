import streamlit as st
import os
import yt_dlp
import whisper
import pandas as pd
import csv
from googleapiclient.discovery import build
from datetime import datetime
from urllib.parse import urlparse
import openpyxl  # Ensure you have openpyxl installed: pip install openpyxl

# -----------------------------
# 1. Timestamp Helper
# -----------------------------
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# 2. Language Code Mapping
# -----------------------------
def get_language_code(selected_language):
    language_map = {
        "Kannada": "kn",
        "Hindi": "hi",
        "Tamil": "ta",
        "Marathi": "mr",
        "Gujarati": "gu",
        "Punjabi": "pa",
        "Bengali": "bn",
    }
    return language_map.get(selected_language, None)

# -----------------------------
# 3. Convert Handle/URL -> Channel ID
# -----------------------------
def get_channel_id_from_handle(youtube_url_or_handle, api_key):
    """
    Extracts the handle from a URL like 'https://www.youtube.com/@SangamTalks'
    or simply uses the input if it's just '@SangamTalks'.
    Then performs a search via the YouTube Data API to return the channel's ID.
    """
    if youtube_url_or_handle.startswith("http") or youtube_url_or_handle.startswith("www"):
        parsed_url = urlparse(youtube_url_or_handle)
        path = parsed_url.path  # e.g. "/@SangamTalks"
        handle = path.lstrip("/")  # -> "@SangamTalks"
    else:
        handle = youtube_url_or_handle

    if not handle.startswith("@"):  # Ensure it starts with '@'
        st.error("Invalid handle. It should start with '@' (e.g. '@SangamTalks').")
        return None

    search_query = handle[1:]  # Remove '@' for the query

    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.search().list(
        q=search_query,
        type="channel",
        part="id",
        maxResults=1
    ).execute()

    items = response.get("items", [])
    if not items:
        st.error("Could not find a channel matching that handle.")
        return None

    # Extract the channel ID
    return items[0]["id"]["channelId"]

# -----------------------------
# 4. Get *All* Video IDs
# -----------------------------
def get_all_video_ids(channel_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,  # Max allowed by the API per call
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            if item['id']['kind'] == 'youtube#video':
                video_ids.append(item['id']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

# -----------------------------
# 5. Download Audio
# -----------------------------
def download_youtube_audio(video_id, output_path='.'):
    """
    Downloads the audio of a given YouTube video if it doesn't already exist.
    """
    try:
        os.makedirs(output_path, exist_ok=True)
        audio_file_path = os.path.join(output_path, f"{video_id}.mp3")

        # Check if the file already exists
        if os.path.exists(audio_file_path):
            st.info(f"[{get_timestamp()}] Skipping download for video ID {video_id}. File already exists.")
            return audio_file_path  # Return the existing file path

        # File doesn't exist, proceed to download
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, f'{video_id}.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return audio_file_path  # Return the path of the downloaded file

    except Exception as e:
        st.error(f"[{get_timestamp()}] Error while downloading audio for video ID {video_id}: {e}")
        return None

# -----------------------------
# 6. Transcribe Audio
# -----------------------------
def transcribe_audio_if_not_done(audio_file, video_id, language_code, output_path):
    """
    Checks if transcription for this audio file already exists.
    If it does, skips transcription. Otherwise, transcribes and saves the result.
    """
    try:
        # Define a path for the transcript file
        transcript_file_path = os.path.join(output_path, f"{video_id}_transcription.csv")

        # Check if transcription already exists
        if os.path.exists(transcript_file_path):
            st.info(f"[{get_timestamp()}] Skipping transcription for video ID {video_id}. Transcript already exists.")
            return pd.read_csv(transcript_file_path)

        # Perform transcription as it doesn't exist
        model = whisper.load_model("turbo")
        result = model.transcribe(audio_file, language=language_code)

        # Save transcription to a CSV file
        with open(transcript_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Video ID", "Start Time (s)", "End Time (s)", "Transcript"])
            for segment in result["segments"]:
                writer.writerow([
                    video_id,
                    round(segment["start"], 2),
                    round(segment["end"], 2),
                    segment["text"]
                ])

        # Load the saved transcript into a DataFrame
        return pd.DataFrame(
            [
                [video_id, round(segment["start"], 2), round(segment["end"], 2), segment["text"]]
                for segment in result["segments"]
            ],
            columns=["Video ID", "Start Time (s)", "End Time (s)", "Transcript"],
        )

    except Exception as e:
        st.error(f"[{get_timestamp()}] Error while transcribing audio for video ID {video_id}: {e}")
        return None

# -----------------------------
# 7. Streamlit App
# -----------------------------
st.title("YouTube Channel Audio Downloader and Multi-Language Transcriber")

# 7a. Input: YouTube handle/URL and API Key
youtube_input = st.text_input(
    "Enter YouTube channel handle or URL (e.g. '@SangamTalks' or 'https://www.youtube.com/@SangamTalks')",
    value=""
)
api_key = st.text_input("Enter YouTube Data API Key", type="password")

# 7b. Language selection
selected_language = st.selectbox(
    "Select transcription language",
    ["Kannada", "Hindi", "Tamil", "Marathi", "Gujarati", "Punjabi", "Bengali"]
)
language_code = get_language_code(selected_language)

# 7c. Output directory
output_path = "audio_files"

# 7d. Dictionary to store each video's transcripts as a separate DataFrame
all_video_dfs = {}

# 7e. Process Channel
if st.button("Process Channel"):
    if youtube_input and api_key:
        # Initialize failed_videos list
        failed_videos = []

        # 1. Convert handle/URL -> channel_id
        with st.spinner(f"[{get_timestamp()}] Resolving channel handle/URL..."):
            channel_id = get_channel_id_from_handle(youtube_input, api_key)

        if channel_id:
            st.success(f"[{get_timestamp()}] Resolved Channel ID: {channel_id}")

            # 2. Fetch video IDs
            with st.spinner(f"[{get_timestamp()}] Fetching all video IDs for channel..."):
                video_ids = get_all_video_ids(channel_id, api_key)

            if video_ids:
                st.success(f"[{get_timestamp()}] Found {len(video_ids)} videos. Processing all of them...")

                # 3. Loop through each video
                for idx, video_id in enumerate(video_ids, start=1):
                    with st.spinner(f"[{get_timestamp()}] [{idx}/{len(video_ids)}] Processing video ID: {video_id}"):
                        try:
                            # Step 1: Check and download audio
                            audio_file = download_youtube_audio(video_id, output_path)
                            if not audio_file:
                                raise Exception(f"Audio download failed for video ID: {video_id}")

                            # Step 2: Check and transcribe audio
                            df_video = transcribe_audio_if_not_done(audio_file, video_id, language_code, output_path)
                            if df_video is None:
                                raise Exception(f"Transcription failed or was skipped for video ID: {video_id}")

                            # Step 3: Store transcript DataFrame in dictionary
                            all_video_dfs[video_id] = df_video

                        except Exception as e:
                            # Log the error and add the video ID to the failed list
                            st.error(f"[{get_timestamp()}] Error for video ID {video_id}: {e}")
                            failed_videos.append(video_id)

                # 4. After looping through all videos, create single Excel with multiple sheets
                if all_video_dfs:
                    # Ensure the output folder exists
                    os.makedirs(output_path, exist_ok=True)

                    excel_filename = os.path.join(output_path, "all_transcripts_multisheet.xlsx")

                    # Write each video's DataFrame to its own sheet
                    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                        for vid_id, df_vid in all_video_dfs.items():
                            sheet_name = vid_id[:31]  # Truncate sheet name if necessary
                            df_vid.to_excel(writer, sheet_name=sheet_name, index=False)

                    st.success(f"[{get_timestamp()}] All transcripts saved to {excel_filename} (multi-sheet).")

                    # Provide a download button for this single Excel file
                    with open(excel_filename, "rb") as f:
                        st.download_button(
                            label="📅 Download Multi-Sheet Excel",
                            data=f.read(),
                            file_name="all_transcripts_multisheet.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                else:
                    st.info("No transcripts to save. Possibly no segments found.")
            else:
                st.error(f"[{get_timestamp()}] No videos found in the channel.")
    else:
        st.error(f"[{get_timestamp()}] Please enter a valid channel handle/URL and API Key.")
