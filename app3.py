
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # Load all the environment variables
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for the Google Gemini API
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Common language codes for reference
language_codes = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Urdu": "ur",
    "Chinese (Simplified)": "zh",
    "Chinese (Traditional)": "zh-Hant",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Italian": "it",
    "Turkish": "tr",
    "Dutch": "nl",
}


# Function to extract transcript details
def extract_transcript_details(youtube_video_url, language="en"):
    try:
        video_id = youtube_video_url.split("=")[1]

        # Get available transcript languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [t.language_code for t in transcript_list]

        if language not in available_languages:
            return f"Transcript not available in {language}. Available languages: {', '.join(available_languages)}"

        # Get the transcript in the specified language
        transcript_text = transcript_list.find_transcript([language]).fetch()
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "No transcript found for this video."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Function to generate summary using Google Gemini API
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


# Streamlit App
st.title("YouTube Transcript to Detailed Notes Converter")

# Sidebar: Language Codes
st.sidebar.title("Language Codes Reference")
st.sidebar.write("Use the following language codes when selecting your desired language:")
for language, code in language_codes.items():
    st.sidebar.write(f"- **{language}:** `{code}`")

# User inputs
youtube_link = st.text_input("Enter YouTube Video Link:")
language = st.text_input("Enter Language Code (e.g., 'en' for English, 'es' for Spanish):", "en")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Get Detailed Notes"):
    # Get the transcript
    transcript_text = extract_transcript_details(youtube_link, language)

    if transcript_text.startswith("Transcript not available"):
        st.warning(transcript_text)
    elif "Transcripts are disabled" in transcript_text or "No transcript found" in transcript_text:
        st.error(transcript_text)
    else:
        # Generate the summary
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
