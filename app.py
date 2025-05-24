import streamlit as st
from gtts import gTTS
import speech_recognition as sr
import Levenshtein
import os
import uuid
import openai
import time 

from dotenv import load_dotenv
load_dotenv()


def transcribe_audio_openai(audio_path):
    """
    Transcribes audio using OpenAI Whisper STT with enhanced logging and timeout.
    Args:
        audio_path (str): Path to the input audio file.
    Returns:
        str: The transcribed text or None if an error occurs.
    """
    st.info("Preparing to transcribe with OpenAI...")
    print("\n--- Starting OpenAI Transcription ---", flush=True)
    print(f"Audio file path: {audio_path}", flush=True)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("OpenAI API key not found! Please set the OPENAI_API_KEY environment variable.")
        print("ERROR: OPENAI_API_KEY environment variable not set.", flush=True)
        return None

    print(f"OpenAI API key found (starts with: {api_key[:5]}...).", flush=True) # Print first 5 chars

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        st.error(f"Audio file not found or is empty: {audio_path}")
        print(f"ERROR: Audio file not found or is empty: {audio_path}", flush=True)
        return None

    print(f"Audio file size: {os.path.getsize(audio_path)} bytes.", flush=True)

    try:
        print("Initializing OpenAI client with timeout...", flush=True)
        # Add a timeout (e.g., 30 seconds)
        client = openai.OpenAI(api_key=api_key, timeout=30.0)
        print("OpenAI client initialized.", flush=True)

        print(f"Attempting to open file: {audio_path}", flush=True)
        with open(audio_path, "rb") as audio_file:
            print(f"File {audio_path} opened successfully.", flush=True)
            st.info("Uploading audio to OpenAI (can take a moment)...")
            print("Sending request to OpenAI STT API...", flush=True)
            
            start_time = time.time() # Track time
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="de"
            )
            end_time = time.time() # Track time

            st.info("Received response from OpenAI.")
            print(f"Received response from OpenAI STT API (took {end_time - start_time:.2f} seconds).", flush=True)
            transcript = response.text
            print(f"Transcription successful: {transcript}", flush=True)
            print("--- Finished OpenAI Transcription ---", flush=True)
            return transcript

    except openai.APITimeoutError:
        st.error("OpenAI API call timed out. The server didn't respond in 30 seconds. Check network or OpenAI status.")
        print("ERROR: OpenAI API Timeout.", flush=True)
        return None
    except openai.APIConnectionError as e:
        st.error(f"OpenAI API Connection Error: {e}")
        print(f"ERROR: OpenAI API Connection Error: {e}", flush=True)
        return None
    except openai.RateLimitError as e:
        st.error(f"OpenAI Rate Limit Exceeded: {e}")
        print(f"ERROR: OpenAI Rate Limit Error: {e}", flush=True)
        return None
    except openai.APIStatusError as e:
        st.error(f"OpenAI API Status Error: {e.status_code} - {e.response}.")
        print(f"ERROR: OpenAI API Status Error: {e.status_code} - {e.response}", flush=True)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred with OpenAI STT: {e}")
        print(f"ERROR: An unexpected error occurred: {e}", flush=True)
        return None

german_phrases = {
    "Wie geht es Ihnen?": "Wie geht es Ihnen?",
    "Ich heiße...": "Ich heiße...",
    "Können Sie mir helfen?": "Können Sie mir helfen?",
    "Wo ist die Toilette?": "Wo ist die Toilette?",
    "Ich brauche einen Arzt.": "Ich brauche einen Arzt."
}

def get_similarity_score(original, transcribed):
    if not transcribed: return 0
    distance = Levenshtein.distance(original.lower(), transcribed.lower())
    max_len = max(len(original), len(transcribed))
    return round((1 - distance / max_len) * 100, 2)

def get_feedback_color(score):
    if score >= 80: return "green"
    elif score >= 60: return "orange"
    else: return "red"

def text_to_speech(text, lang='de', filename="temp_audio.mp3"):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error in Text-to-Speech: {e}")
        return None

# --- Record and Save Audio (Kept the same) ---
def record_and_save_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Adjusting for ambient noise...")
        print("Adjusting for ambient noise...")
        try:
            r.adjust_for_ambient_noise(source, duration=1)
            st.info("Please speak now...")
            print("Listening...")
            r.pause_threshold = 0.8
            audio_data = r.listen(source, timeout=5, phrase_time_limit=10)
            st.info("Processing...")
            print("Finished listening. Processing audio...")

            temp_filename = f"temp_recording_{uuid.uuid4()}.wav"
            print(f"Attempting to save audio to: {temp_filename}")

            with open(temp_filename, "wb") as f:
                f.write(audio_data.get_wav_data())

            print(f"Audio saved successfully to {temp_filename}")
            return temp_filename

        except sr.WaitTimeoutError:
            st.warning("No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.warning("Sorry, I could not understand that (microphone).")
            return None
        except sr.RequestError as e:
            st.error(f"Microphone/Speech recognition service error; {e}")
            return None
        except Exception as e:
            st.error(f"An error occurred during recording: {e}")
            return None

# --- Streamlit App UI ---
st.title("🇩🇪 German Pronunciation Practice for Nurses 🇩🇪")

st.markdown("Select a preset phrase, or enter your own below.")

# --- Phrase Selection Logic ---
selected_preset = st.selectbox("Select a preset phrase:", list(german_phrases.keys()))
custom_sentence = st.text_input("Or enter your own sentence here:")

# Determine the active sentence
if custom_sentence.strip():
    active_sentence = custom_sentence.strip()
    st.session_state.active_sentence = active_sentence
else:
    active_sentence = selected_preset
    st.session_state.active_sentence = active_sentence

# Display the currently active sentence
st.info(f"**Currently Practicing:** {st.session_state.active_sentence}")

# --- Listen and Record Buttons ---
if st.button("Listen to Phrase 🎧"):
    if st.session_state.active_sentence:
        audio_file = text_to_speech(st.session_state.active_sentence)
        if audio_file:
            st.audio(audio_file)
            try: os.remove(audio_file)
            except: pass
    else:
        st.warning("Please select or enter a sentence first.")


st.markdown("---")
st.subheader("Your Pronunciation:")

if "transcribed_text" not in st.session_state: st.session_state.transcribed_text = ""
if "similarity_score" not in st.session_state: st.session_state.similarity_score = 0.0

if st.button("Record and Transcribe 🎤"):
    current_sentence_to_practice = st.session_state.get('active_sentence', None)

    if not current_sentence_to_practice:
        st.warning("No active sentence to practice. Please select or enter one.")
    else:
        audio_file_path = record_and_save_audio()
        transcribed_text = None
        if audio_file_path:
            transcribed_text = transcribe_audio_openai(audio_file_path)
            try: os.remove(audio_file_path)
            except Exception as e: print(f"Error removing temp file {audio_file_path}: {e}")

        if transcribed_text is not None:
            st.session_state.transcribed_text = transcribed_text
            st.session_state.similarity_score = get_similarity_score(current_sentence_to_practice, transcribed_text)
        else:
            st.session_state.transcribed_text = ""
            st.session_state.similarity_score = 0.0
        st.rerun()

# --- Feedback Display ---
if st.session_state.transcribed_text:
    st.markdown(f"**Your Transcription:** {st.session_state.transcribed_text}")
    score = st.session_state.similarity_score
    score_color = get_feedback_color(score)
    st.markdown(f"**Similarity Score:** <span style='color:{score_color}; font-size: 20px;'>{score}%</span>", unsafe_allow_html=True)
    if score >= 80: st.success("Very good! Keep it up! 👍")
    elif score >= 60: st.warning("Not bad, but you can do better! Try again. 😊")
    else: st.error("This needs a bit more practice. Try again! 💪")

if st.button("Try Again 🔁"):
    st.session_state.transcribed_text = ""
    st.session_state.similarity_score = 0.0
    st.rerun()

# --- Sidebar ---
st.markdown("---")
st.sidebar.title("About this Project")
st.sidebar.info(
    "This tool helps nurses practice their German pronunciation. "
    "It uses Google Text-to-Speech for playback and OpenAI Whisper "
    "for transcription. Similarity is calculated using the Levenshtein distance."
)