import streamlit as st
import requests
import csv
import os
import yt_dlp


# Function to download audio from YouTube
def download_youtube_audio(url, output_path="audio_files"):
    try:
        os.makedirs(output_path, exist_ok=True)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict["id"]
            filename = os.path.join(output_path, f"{video_id}.mp3")
            return video_id, filename
    except Exception as e:
        st.error(f"An error occurred while downloading audio: {e}")
        return None, None


# Function to transcribe audio using the API
def transcribe_audio(file_path, language="hindi"):
    try:
        with open(file_path, 'rb') as audio_file:
            files = {
                'file': audio_file,
                'language': (None, language),
                'vtt': (None, 'true'),
            }
            response = requests.post('https://asr.iitm.ac.in/internal/asr/decode', files=files)
            if response.status_code == 200:
                return response.json()  # Returns a JSON response with transcript and VTT
            else:
                st.error(f"Error during transcription: {response.text}")
                return None
    except Exception as e:
        st.error(f"An error occurred while transcribing: {e}")
        return None


# Function to parse VTT and save transcription to CSV
def save_transcription_to_csv(video_id, vtt_text, output_path="transcription.csv"):
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Video ID", "Start Time (s)", "End Time (s)", "Transcript"])  # CSV headers

            # Parse the VTT content
            lines = vtt_text.splitlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:  # Look for the timestamp line
                    # Extract timestamps
                    times = lines[i].split(" --> ")
                    start_time = convert_vtt_time_to_seconds(times[0])
                    end_time = convert_vtt_time_to_seconds(times[1])

                    # Extract the transcript text
                    transcript = lines[i + 1] if i + 1 < len(lines) else ""

                    # Write to CSV
                    writer.writerow([
                        f"https://youtu.be/{video_id}",
                        round(start_time, 2),  # Start time in seconds
                        round(end_time, 2),    # End time in seconds
                        transcript.strip()     # Remove extra spaces
                    ])
        return output_path
    except Exception as e:
        st.error(f"An error occurred while saving to CSV: {e}")
        return None


# Function to convert VTT time format to seconds
def convert_vtt_time_to_seconds(vtt_time):
    h, m, s = vtt_time.split(":")
    s, ms = map(float, s.split("."))
    return int(h) * 3600 + int(m) * 60 + s + ms / 1000


# Streamlit App
st.title("YouTube Audio Transcription")

# Input YouTube URL
youtube_url = st.text_input("Enter YouTube Video URL", "")

# Language selection
languages = {
    "hindi": "Hindi",
    "tamil": "Tamil",
    "kannada": "Kannada",
    "telugu": "Telugu",
    "malayalam": "Malayalam"
}
selected_language = st.selectbox("Select Language for Transcription", list(languages.keys()), format_func=lambda x: languages[x])

# Process button
if st.button("Transcribe and Save"):
    if youtube_url and selected_language:
        # Step 1: Download the audio from YouTube
        st.info("Downloading audio from YouTube...")
        video_id, audio_file_path = download_youtube_audio(youtube_url)

        if audio_file_path:
            st.success(f"Audio downloaded successfully: {audio_file_path}")

            # Step 2: Transcribe the audio
            st.info("Transcribing audio, please wait...")
            transcription_result = transcribe_audio(audio_file_path, selected_language)

            if transcription_result:
                st.success("Transcription completed successfully!")

                # Debugging: Display the JSON response
                st.json(transcription_result)

                # Step 3: Save transcription to CSV
                st.info("Saving transcription to CSV...")
                vtt_text = transcription_result.get("vtt", "")
                if vtt_text:
                    csv_file_path = save_transcription_to_csv(video_id, vtt_text)
                    if csv_file_path:
                        st.success(f"Transcription saved to CSV: {csv_file_path}")

                        # Step 4: Provide download button for CSV
                        with open(csv_file_path, "rb") as csv_file:
                            st.download_button(
                                label="📥 Download Transcription CSV",
                                data=csv_file,
                                file_name=f"{video_id}_transcription.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error("Failed to save transcription to CSV.")
                else:
                    st.error("VTT content is missing from the transcription result.")
            else:
                st.error("Failed to transcribe the audio.")
        else:
            st.error("Failed to download audio.")
    else:
        st.error("Please provide both a YouTube URL and select a language.")

