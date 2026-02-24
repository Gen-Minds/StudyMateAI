import streamlit as st
import pandas as pd
import datetime
import os
import random
import matplotlib.pyplot as plt

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="StudyMate AI", layout="centered")

# ------------------ SESSION STATE ------------------
if "emotion" not in st.session_state:
    st.session_state.emotion = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

# ------------------ FILES ------------------
USER_FILE = "users.csv"

# ------------------ USER FUNCTIONS ------------------
def register_user(username, password):
    if os.path.exists(USER_FILE):
        users = pd.read_csv(USER_FILE)
        if username in users["username"].values:
            return False
        new_user = pd.DataFrame({"username": [username], "password": [password]})
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_csv(USER_FILE, index=False)
    else:
        new_user = pd.DataFrame({"username": [username], "password": [password]})
        new_user.to_csv(USER_FILE, index=False)
    return True

def login_user(username, password):
    if os.path.exists(USER_FILE):
        users = pd.read_csv(USER_FILE)
        user = users[(users["username"] == username) & (users["password"] == password)]
        if not user.empty:
            return True
    return False

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:

    st.title("🔐 StudyMate AI")

    menu = st.radio("Select Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Register":
        if st.button("Create Account"):
            if username and password:
                if register_user(username, password):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username already exists.")
            else:
                st.warning("Please enter username and password.")

    if menu == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.stop()

# ------------------ SIDEBAR ------------------
st.sidebar.title("📘 StudyMate AI")
st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

page = st.sidebar.radio("Navigate", ["Home", "Emotion History"])

# ------------------ EMOJI MAP ------------------
emoji_map = {
    "Happy": "😃",
    "Sad": "😔",
    "Anxiety": "😰",
    "Bored": "😴",
    "Neutral": "😐"
}

# ------------------ FUNCTIONS ------------------
def detect_emotion(text):
    text = text.lower()

    # Anxiety keywords
    anxiety_words = [
        "stress", "tension", "anxious", "pressure",  # English
        "tension undi", "bhayam", "bayam", "naaku bhayam", "tanav",  # Telugu/Hindi
        "dar lag raha", "mujhe tanav hai"
    ]

    # Sad keywords
    sad_words = [
        "sad", "low", "upset", "disappointed",  # English
        "baadha", "dukham", "dukhi", "naaku baadha ga undi",  # Telugu
        "mujhe dukhi lag raha"
    ]

    # Happy keywords
    happy_words = [
        "happy", "excited", "confident", "great", "success",  # English
        "santhosham", "santosham", "khushi", "naaku santhosham ga undi",  # Telugu
        "mujhe khushi ho rahi hai"
    ]

    # Bored keywords
    bored_words = [
        "bored", "boring", "tired", "lazy", "uninterested",  # English
        "visugu", "bor ho raha", "nenu visugu padutunnanu"  # Telugu/Hindi
    ]

    if any(word in text for word in anxiety_words):
        return "Anxiety"
    elif any(word in text for word in sad_words):
        return "Sad"
    elif any(word in text for word in happy_words):
        return "Happy"
    elif any(word in text for word in bored_words):
        return "Bored"
    else:
        return "Neutral"

def give_suggestion(emotion):
    suggestions = {
        "Anxiety": "Take a 5-minute breathing break and start with an easy topic.",
        "Sad": "Listen to motivational music and revise a simple chapter.",
        "Happy": "Great! Try solving difficult problems now.",
        "Bored": "Switch to a different subject for 30 minutes.",
        "Neutral": "Maintain steady study pace."
    }
    return suggestions.get(emotion, "Stay focused.")

def chatbot_reply(emotion):
    replies = {
        "Anxiety": "I understand you're feeling anxious. Try deep breathing.",
        "Sad": "One bad day doesn't define you. Keep going.",
        "Happy": "Awesome! Use this energy productively.",
        "Bored": "Try a quick 10-minute challenge.",
        "Neutral": "Tell me more. I'm here to help."
    }
    return replies.get(emotion, "I'm here for you.")

quotes = [
    "Success is built on small daily efforts.",
    "You are stronger than your stress.",
    "Focus today, achieve tomorrow.",
    "Consistency beats intensity.",
    "Small progress is still progress.",
    "Dream big, work hard, stay consistent.",
    "Your only limit is your mindset."
]

# ================== HOME ==================
if page == "Home":

    st.markdown("<h1 style='text-align: center;'>🤖 StudyMate AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Emotion-Aware Study Companion</p>", unsafe_allow_html=True)

    st.info("This system analyzes your emotional state and provides personalized study suggestions.")

    user_input = st.text_area("How are you feeling today? (English, Telugu, Hindi supported)")

    if st.button("Analyze Emotion"):

        emotion = detect_emotion(user_input)
        st.session_state.emotion = emotion

        filename = f"{st.session_state.username}_emotion_history.csv"

        data = {
            "Date": [datetime.datetime.now()],
            "Emotion": [emotion]
        }

        df = pd.DataFrame(data)

        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)

    if st.session_state.emotion:

        emotion = st.session_state.emotion
        suggestion = give_suggestion(emotion)

        st.markdown(f"### Detected Emotion: {emoji_map.get(emotion)} {emotion}")

        if emotion == "Happy":
            st.success(suggestion)
        elif emotion == "Sad":
            st.info(suggestion)
        elif emotion == "Anxiety":
            st.warning(suggestion)
        elif emotion == "Bored":
            st.info(suggestion)
        else:
            st.write(suggestion)

        st.info("Chatbot: " + chatbot_reply(emotion))

    if st.button("Generate Motivation"):
        st.success(random.choice(quotes))

    user_chat = st.text_input("Chat with StudyMate AI", key="chat_input")

    if user_chat:
        st.write("StudyMate AI: Tell me more. I'm here to support you.")

# ================== EMOTION HISTORY ==================
elif page == "Emotion History":

    st.header("📊 Emotion History & Analytics")

    filename = f"{st.session_state.username}_emotion_history.csv"

    if os.path.exists(filename):

        history = pd.read_csv(filename)
        st.dataframe(history)

        emotion_counts = history["Emotion"].value_counts()

        st.subheader("Emotion Distribution")

        fig, ax = plt.subplots()
        emotion_counts.plot(kind='bar', ax=ax)
        st.pyplot(fig)

        if st.button("🗑 Clear History"):
            os.remove(filename)
            st.success("Emotion history cleared!")

    else:
        st.write("No history found.")