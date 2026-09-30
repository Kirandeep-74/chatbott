import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Gemini ChatBot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# --------------------------------------------------
# CHECK API KEY
# --------------------------------------------------

if not API_KEY:
    st.error("❌ Gemini API key not found.")
    st.info(
        "Please add GEMINI_API_KEY=your_key_here "
        "inside the .env file."
    )
    st.stop()

# --------------------------------------------------
# GEMINI CLIENT
# --------------------------------------------------

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: linear-gradient(
            135deg,
            #f5f7ff 0%,
            #eef2ff 50%,
            #f8f9ff 100%
        );
    }

    /* Header */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
        color: #4f46e5;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #64748b;
        margin-bottom: 30px;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 12px;
        margin-bottom: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 10px;
        font-weight: 600;
    }

    /* Input */
    [data-testid="stChatInput"] {
        border-radius: 18px;
    }

    /* Welcome card */
    .welcome-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    .feature-card {
        background: white;
        padding: 18px;
        border-radius: 15px;
        margin: 8px 0px;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.05);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🤖 Gemini ChatBot")

    st.markdown("---")

    st.markdown("### ✨ Features")

    st.markdown(
        """
        <div class="feature-card">
        💬 <b>Smart Conversations</b><br>
        Ask questions and get AI-powered answers.
        </div>

        <div class="feature-card">
        🧠 <b>Gemini AI</b><br>
        Powered by Google's Gemini model.
        </div>

        <div class="feature-card">
        ⚡ <b>Fast Responses</b><br>
        Get answers quickly and easily.
        </div>

        <div class="feature-card">
        🔐 <b>Private API Key</b><br>
        Your key is loaded from the .env file.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    if st.button("🧹 Clear Chat"):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    st.caption("💡 Tip")
    st.caption(
        "Ask me about Python, AI, ML, DBMS, "
        "web development, projects and more!"
    )

# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 Gemini AI ChatBot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your friendly AI assistant powered by Gemini ✨'
    '</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# WELCOME SCREEN
# --------------------------------------------------

if len(st.session_state.messages) == 0:

    st.markdown(
        """
        <div class="welcome-card">

        <h2>👋 Hello! I'm your AI Assistant</h2>

        <p>
        Ask me anything and I'll try my best to help you.
        </p>

        <p>
        💻 Coding &nbsp; | &nbsp;
        🤖 AI/ML &nbsp; | &nbsp;
        📚 Study &nbsp; | &nbsp;
        💡 Ideas
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 💡 Try asking")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("🐍 Learn Python"):
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "Teach me Python from beginner level."
                }
            )
            st.rerun()

        if st.button("🤖 What is AI?"):
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "Explain Artificial Intelligence in simple words."
                }
            )
            st.rerun()

    with col2:

        if st.button("📊 Learn Machine Learning"):
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "Explain Machine Learning with a simple example."
                }
            )
            st.rerun()

        if st.button("💡 Project Ideas"):
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "Give me some beginner-friendly AI and ML project ideas."
                }
            )
            st.rerun()

# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👩‍💻"
        ):
            st.markdown(message["content"])

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):
            st.markdown(message["content"])

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

prompt = st.chat_input(
    "💬 Type your message here..."
)

# --------------------------------------------------
# PROCESS USER MESSAGE
# --------------------------------------------------

if prompt:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Display user message
    with st.chat_message(
        "user",
        avatar="👩‍💻"
    ):
        st.markdown(prompt)

    # Create conversation history
    conversation = []

    for message in st.session_state.messages:

        conversation.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )

    # Ask Gemini
    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner("✨ Gemini is thinking..."):

            try:

                # Convert messages into Gemini format
                contents = []

                for message in conversation:

                    role = message["role"]

                    if role == "assistant":
                        role = "model"

                    contents.append(
                        {
                            "role": role,
                            "parts": [
                                {
                                    "text": message["content"]
                                }
                            ]
                        }
                    )

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=contents
                )

                answer = response.text

                st.markdown(answer)

                # Save AI response
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                st.error(
                    "❌ Something went wrong while connecting to Gemini."
                )

                st.caption(
                    f"Error details: {str(e)}"
                )