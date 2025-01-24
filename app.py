import streamlit as st
import os
import yt_dlp
import whisper
import csv
from googleapiclient.discovery import build
from datetime import datetime

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
# 3. Get Channel ID from Handle
# -----------------------------
def get_channel_id_from_handle(youtube_url_or_handle, api_key):
    """
    Extracts the handle from a URL like 'https://www.youtube.com/@SangamTalks'
    or simply uses the input if it's just '@SangamTalks'.
    Then performs a search via the YouTube Data API to return the channel's ID.
    """
    from urllib.parse import urlparse

    # If user enters the handle with or without 'www.youtube.com'
    if youtube_url_or_handle.startswith("http") or youtube_url_or_handle.startswith("www"):
        parsed_url = urlparse(youtube_url_or_handle)
        path = parsed_url.path  # e.g. "/@SangamTalks"
        handle = path.lstrip("/")  # remove leading slash -> "@SangamTalks"
    else:
        handle = youtube_url_or_handle

    if not handle.startswith("@"):
        st.error("Invalid handle. It should start with '@' (e.g. '@SangamTalks').")
        return None

    search_query = handle[1:]

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
    channel_id = items[0]["id"]["channelId"]
    return channel_id

# -----------------------------
# 4. Get *All* Video IDs
# -----------------------------
def get_all_video_ids(channel_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = []
    next_page_token = None

    # Keep fetching until all are retrieved
    while True:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,  # up to 50 per call
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
    try:
        os.makedirs(output_path, exist_ok=True)
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
        return os.path.join(output_path, f"{video_id}.mp3")
    except Exception as e:
        st.error(f"[{get_timestamp()}] Error while downloading audio for video ID {video_id}: {e}")
        return None

# -----------------------------
# 6. Transcribe Audio
# -----------------------------
def transcribe_audio(audio_file, language_code):
    try:
        model = whisper.load_model("large")
        result = model.transcribe(audio_file, language=language_code)
        return result
    except Exception as e:
        st.error(f"[{get_timestamp()}] Error while transcribing audio: {e}")
        return None

# -----------------------------
# 7. Streamlit App
# -----------------------------
st.title("YouTube Channel Audio Downloader and Multi-Language Transcriber")

# 7a. Input YouTube Handle/URL and API Key
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

# 7c. Output directory for audio files
output_path = "audio_files"

# 7d. Button to Process
if st.button("Process Channel"):
    if youtube_input and api_key:
        # Convert handle/URL -> channel_id
        with st.spinner(f"[{get_timestamp()}] Trying to resolve channel handle/URL..."):
            channel_id = get_channel_id_from_handle(youtube_input, api_key)

        # If resolved, proceed
        if channel_id:
            st.success(f"[{get_timestamp()}] Resolved Channel ID: {channel_id}")

            # Fetch all videos
            with st.spinner(f"[{get_timestamp()}] Fetching all video IDs for channel..."):
                video_ids = get_all_video_ids(channel_id, api_key)

            if video_ids:
                st.success(f"[{get_timestamp()}] Found {len(video_ids)} videos. Processing all of them...")

                # Loop through each video
                for video_id in video_ids:
                    with st.spinner(f"[{get_timestamp()}] Processing video ID: {video_id}"):
                        audio_file = download_youtube_audio(video_id, output_path)
                        if audio_file:
                            st.success(f"[{get_timestamp()}] Audio downloaded for video ID: {video_id}")
                            try:
                                result = transcribe_audio(audio_file, language_code)

                                if result:
                                    # Save transcription and timestamps to CSV
                                    csv_filename = os.path.join(output_path, f"{video_id}_transcription.csv")
                                    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                                        writer = csv.writer(file)
                                        writer.writerow(["Video ID", "Start Time (s)", "End Time (s)", "Transcript"])
                                        for segment in result["segments"]:
                                            writer.writerow([
                                                video_id,
                                                round(segment["start"], 2),
                                                round(segment["end"], 2),
                                                segment["text"]
                                            ])

                                    st.success(f"[{get_timestamp()}] Transcription saved to {csv_filename}")
                                    st.download_button(
                                        label="📥 Download Transcription CSV",
                                        data=open(csv_filename, "r"),
                                        file_name=f"{video_id}_transcription.csv",
                                        mime="text/csv",
                                    )
                            except Exception as e:
                                st.error(f"[{get_timestamp()}] Error during transcription: {e}")
                        else:
                            st.error(f"[{get_timestamp()}] Audio download failed for video ID: {video_id}")
            else:
                st.error(f"[{get_timestamp()}] No videos found in the channel.")
    else:
        st.error(f"[{get_timestamp()}] Please enter a valid channel handle/URL and API Key.")
