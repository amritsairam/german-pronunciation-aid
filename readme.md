# German Pronunciation Aid for Nurses 🇩🇪👩‍⚕️

A browser-based prototype to help German-learning nurses practice their pronunciation and get instant feedback.

## 🚀 The Goal

Many nurses learning German struggle with spoken practice. This tool provides an accessible way to:
1.  Listen to common German phrases.
2.  Record themselves speaking the phrase.
3.  Receive instant feedback via transcription and a similarity score.

## ✨ Features

* **Preset Phrases:** Select from a list of 5 common German phrases.
* **Custom Input:** Enter *any* German sentence for practice.
* **Text-to-Speech:** Listen to native-like pronunciation (`gTTS`).
* **Speech-to-Text:** High-quality transcription using OpenAI's Whisper API.
* **Similarity Score:** Get a percentage score based on Levenshtein distance.
* **Instant Feedback:** Color-coded scores for quick assessment.
* **Retry Option:** Practice a phrase multiple times to see improvement.

## 🛠️ Tech Stack Used

* **Framework:** Streamlit (for rapid web app development)
* **Speech Recognition (Recording):** `speech_recognition` + `pyaudio`
* **Speech-to-Text (Transcription):** OpenAI Whisper API (`openai`)
* **Text-to-Speech (Playback):** Google Text-to-Speech (`gTTS`)
* **Similarity Calculation:** `python-Levenshtein`
* **Language:** Python 3.x

## 챌 Challenges Faced

* **Environment Setup:** Installing `pyaudio` can be tricky across different operating systems, requiring pre-installation of system libraries like `portaudio` (macOS/Linux) or specific wheel files/build tools (Windows).
* **API Management:**
    * Switching between different STT providers (Google Cloud vs. OpenAI) involved managing different authentication methods (Service Accounts vs. API Keys) and library dependencies.
    * Ensuring API keys are managed securely (using environment variables) is crucial.
* **Real-time Feedback Loop:** Streamlit's rerun-on-interaction model required careful use of `st.session_state` to maintain the user's current phrase, transcription, and score across button clicks.
* **Debugging External APIs:** When API calls (like to OpenAI) hang or fail without clear errors, it requires adding detailed logging, timeouts, and `flush=True` to pinpoint the issue, often related to network, keys, or API status.
* **Audio Format Handling:** Initially considered `pydub` and FFmpeg for audio conversion, but simplified by using `speech_recognition`'s `get_wav_data()` which is directly compatible with OpenAI's API needs (via file save).

## ⬆️ What You'd Need to Go Live

1.  **Robust Hosting:** Deploying the Streamlit app to a service like Streamlit Community Cloud, Heroku, AWS, or Google Cloud.
2.  **Secure API Key Management:** Using a secrets management system provided by the hosting platform (e.g., Streamlit Secrets, environment variables in Heroku/AWS) instead of relying on local environment variables.
3.  **Scalable OpenAI Account:** Ensuring the OpenAI account has appropriate usage limits and billing set up to handle multiple users.
4.  **FFmpeg (Potentially):** If we wanted to support direct uploads of *various* audio formats (beyond microphone WAV), installing FFmpeg on the server would be necessary for robust conversion.
5.  **User Authentication & Database (for Week 2+):** If user tracking is implemented, a database and user login system would be required.
6.  **Domain Name & SSL:** A professional URL with HTTPS.
7.  **Testing & Monitoring:** Rigorous testing across browsers and devices, plus monitoring for errors and API usage.