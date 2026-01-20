import streamlit as st
from textblob import TextBlob
import pandas as pd
from datetime import datetime
import os
from openai import OpenAI
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="Mental Health Support Chatbot", page_icon="🧠")

# Load environment variables
load_dotenv()

st.markdown("<h1 style='text-align:center;'>🧠 Mental Health Support Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>A safe space to share your feelings</p>", unsafe_allow_html=True)


# System Prompt
SYSTEM_PROMPT = """
You are a supportive mental health chatbot.
Always respond kindly and empathetically.
Never give medical or clinical diagnosis.
If the user expresses self-harm or extreme distress, suggest contacting helplines.
Keep responses short and caring.
"""



HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("⚠️ HF_TOKEN not found in .env file")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)
   

# Generate AI Response
def generate_response(prompt):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add last 5 messages for conversational memory
        for role, content in st.session_state.messages[-5:]:
            messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct:novita",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except:
        return "⚠️ I'm having trouble responding. Please try again."



# Sentiment Analysis
def analyze_sentiment(text):
    text_lower = text.lower()
    polarity = TextBlob(text).sentiment.polarity

    # Keyword-based polarity override
    negative_words = ["stress","stressed","anxious","sad","depressed","overwhelmed","angry","panic","worried","fear"]
    positive_words = ["happy","excited","great","good","awesome","love","amazing","confident"]

    if any(word in text_lower for word in negative_words):
        polarity -= 0.6

    if any(word in text_lower for word in positive_words):
        polarity += 0.6

    # Clamp polarity range
    polarity = max(-1, min(1, polarity))

    # Label sentiment
    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity


# Coping Strategy
def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep spreading your positive energy 🌟",
        "Positive": "It's nice to see you're feeling good 🙂",
        "Neutral": "Try doing something you enjoy today 💫",
        "Negative": "Take a deep breath. You're not alone 💙",
        "Very Negative": "I'm here for you. Consider talking to someone you trust 💙"
    }
    return strategies.get(sentiment, "Stay strong 💪")

# Chat Input
user_message = st.chat_input("Type your message...")

# Sidebar Resources
# ----------- Sidebar UI -----------

st.sidebar.markdown("## 🧠 Mental Health Assistant")

st.sidebar.markdown("""
📊 **Mood Tracker**  
Track your emotional trend over time.

🧘 **Therapy Modes**  
Empathetic Chat • Healing Tips • Breathing • Motivation

📥 **Download Report**  
Export your mood summary as PDF / CSV.

🔒 **Privacy Notice**  
Messages are stored only during this session.
They are never saved permanently.
""")

st.sidebar.markdown("---")

# ----------- Smart Crisis Detection -----------

danger_words = [
    "suicide","kill myself","end my life","self harm",
    "want to die","no reason to live","give up"
]

if user_message and any(word in user_message.lower() for word in danger_words):
    st.sidebar.error("""
🚨 **Emergency Support Needed**

If you are in immediate danger or thinking about self-harm,  
please contact a real human support service:

📞 **AASRA (India):** +91-22-27546669  
💬 **iCall:** +91-9152987821  
🌍 **Find a Helpline:** https://findahelpline.com/

You are not alone 💙
""")


# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mood_tracker" not in st.session_state:
    st.session_state.mood_tracker = []

if len(st.session_state.messages) == 0:
    st.markdown("""
    ### 👋 Welcome to Mental Health Support Chatbot  
    Share how you're feeling, and I’ll listen 💙  
    Start by typing below...
    """)


st.markdown("### 💬 Choose Support Mode")

support_mode = st.selectbox(
    "Select how you want me to help:",
    ["Empathetic Chat", "Healing Therapy Tips", "Breathing Exercise", "Motivational Support"]
)

def therapy_module(mode, user_message):
    if mode == "Healing Therapy Tips":
        return (
            "🧘 Try this healing exercise:\n"
            "• Sit comfortably\n"
            "• Close your eyes\n"
            "• Breathe in slowly for 4 seconds\n"
            "• Hold for 4 seconds\n"
            "• Exhale for 6 seconds\n"
            "Repeat 5 times 🌿"
        )
    
    elif mode == "Breathing Exercise":
        return (
            "🌬️ Guided Breathing:\n"
            "Inhale... 4s\n"
            "Hold... 4s\n"
            "Exhale... 6s\n"
            "Repeat this cycle 5 times 💙"
        )
    
    elif mode == "Motivational Support":
        return (
            "✨ You are stronger than you think.\n"
            "Every small step matters.\n"
            "I believe in you 💪"
        )
    
    else:
        return None



if user_message:
    # Store user message
    st.session_state.messages.append(("user", user_message))

    # Sentiment
    sentiment, polarity = analyze_sentiment(user_message)

    # AI Response
    therapy_response = therapy_module(support_mode, user_message)

    if therapy_response:
        bot_response = therapy_response
    else:
        bot_response = generate_response(user_message)


    # Store bot response
    st.session_state.messages.append(("assistant", bot_response))

    # Store mood data
    st.session_state.mood_tracker.append(
        (datetime.now(), sentiment, polarity)
    )


# Display Messages
for sender, message in st.session_state.messages:
    with st.chat_message(sender):
        st.write(message)

# Coping Suggestion
if st.session_state.mood_tracker:
    last_sentiment = st.session_state.mood_tracker[-1][1]
    st.info("💡 Coping Tip: " + provide_coping_strategy(last_sentiment))

if user_message:
    emotion = "🙂 Calm"

    text = user_message.lower()

    if any(word in text for word in ["anxious","nervous","worried","panic","fear"]):
        emotion = "😟 Anxiety"
    elif any(word in text for word in ["sad","depressed","cry","lonely","down","passed away","died","lost","death","grief","funeral"]):
        emotion = "😢 Sadness"
    elif any(word in text for word in ["angry","mad","frustrated","irritated"]):
        emotion = "😡 Anger"
    elif any(word in text for word in ["happy","excited","good","great","awesome","topped"]):
        emotion = "😄 Happiness"
    elif any(word in text for word in ["tired","exhausted","burnout"]):
        emotion = "😴 Fatigue"

    st.markdown(f"**Detected Emotion:** {emotion}")


if st.sidebar.button("📈 Show Mood Summary"):
    if st.session_state.mood_tracker:
        df = pd.DataFrame(st.session_state.mood_tracker, columns=["Time","Sentiment","Polarity"])
        avg = round(df["Polarity"].mean(), 2)
        st.sidebar.success(f"Average Mood Score: {avg}")


# Mood Chart
if st.session_state.mood_tracker:
    df = pd.DataFrame(
        st.session_state.mood_tracker,
        columns=["Time","Sentiment","Polarity"]
    )

    fig = plt.figure()
    plt.plot(df["Time"], df["Polarity"], marker="o")
    plt.title("Mood Polarity Over Time")
    plt.xlabel("Time")
    plt.ylabel("Polarity Score")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close(fig)


