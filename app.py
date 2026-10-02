import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client, Client

st.set_page_config(page_title="Gemini ChatBot", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")
load_dotenv()

def get_secret(name):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")
MODEL_NAME = get_secret("GEMINI_MODEL") or "gemini-3.6-flash"

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY is missing. Add it to Streamlit Secrets or your local .env file.")
    st.stop()
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE_URL or SUPABASE_KEY is missing. Add both to Streamlit Secrets or your local .env file.")
    st.stop()

try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("❌ Could not initialize Gemini or Supabase.")
    st.caption(f"Error details: {e}")
    st.stop()

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#f5f7ff 0%,#eef2ff 50%,#f8f9ff 100%)}
.main-title{text-align:center;font-size:42px;font-weight:800;margin-bottom:5px;color:#4f46e5}
.subtitle{text-align:center;font-size:17px;color:#64748b;margin-bottom:30px}
[data-testid="stChatMessage"]{border-radius:18px;padding:12px;margin-bottom:10px}
[data-testid="stSidebar"]{background:#fff}
.stButton>button{width:100%;border-radius:12px;border:none;padding:10px;font-weight:600}
[data-testid="stChatInput"]{border-radius:18px}
.welcome-card{background:white;padding:25px;border-radius:20px;text-align:center;box-shadow:0 5px 20px rgba(0,0,0,.08);margin-bottom:20px}
.feature-card{background:white;padding:18px;border-radius:15px;margin:8px 0;box-shadow:0 3px 12px rgba(0,0,0,.05)}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE FUNCTIONS ----------------
def create_chat(title="New Chat"):
    result = supabase.table("chats").insert({"title": title}).execute()
    return result.data[0]["id"]

def get_chats():
    result = supabase.table("chats").select("id,title,created_at,updated_at").order("updated_at", desc=True).execute()
    return result.data or []

def load_messages(chat_id):
    result = (supabase.table("messages").select("id,chat_id,role,content,created_at")
              .eq("chat_id", chat_id).order("created_at").execute())
    return result.data or []

def save_message(chat_id, role, content):
    supabase.table("messages").insert({"chat_id": chat_id, "role": role, "content": content}).execute()
    supabase.table("chats").update({"updated_at": "now()"}).eq("id", chat_id).execute()

def rename_chat(chat_id, new_title):
    supabase.table("chats").update({"title": new_title.strip() or "New Chat"}).eq("id", chat_id).execute()

def delete_chat(chat_id):
    supabase.table("chats").delete().eq("id", chat_id).execute()

# ---------------- SESSION STATE ----------------
if "current_chat_id" not in st.session_state:
    try:
        chats = get_chats()
        if chats:
            st.session_state.current_chat_id = chats[0]["id"]
            st.session_state.messages = load_messages(chats[0]["id"])
        else:
            new_id = create_chat()
            st.session_state.current_chat_id = new_id
            st.session_state.messages = []
    except Exception as e:
        st.error("❌ Could not load/create chat in Supabase.")
        st.caption(f"Error details: {e}")
        st.stop()
if "messages" not in st.session_state:
    st.session_state.messages = load_messages(st.session_state.current_chat_id)
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

def start_new_chat():
    new_id = create_chat()
    st.session_state.current_chat_id = new_id
    st.session_state.messages = []
    st.session_state.pending_prompt = None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🤖 Gemini ChatBot")
    st.markdown("---")
    if st.button("➕ New Chat", use_container_width=True):
        try:
            start_new_chat(); st.rerun()
        except Exception as e:
            st.error("Could not create a new chat."); st.caption(str(e))

    st.markdown("### 📚 Chat History")
    try:
        chats = get_chats()
        if chats:
            for chat in chats:
                if st.button(f"💬 {chat.get('title') or 'New Chat'}", key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.current_chat_id = chat["id"]
                    st.session_state.messages = load_messages(chat["id"])
                    st.session_state.pending_prompt = None
                    st.rerun()
        else:
            st.caption("No chats yet.")
    except Exception as e:
        st.error("Could not load chat history."); st.caption(str(e))

    st.markdown("---")
    st.markdown("### ✏️ Chat Management")
    rename_text = st.text_input("New chat name", placeholder="e.g. Python Study Chat", key="rename_text")
    if st.button("✏️ Rename Current Chat", use_container_width=True):
        if rename_text.strip():
            try:
                rename_chat(st.session_state.current_chat_id, rename_text)
                st.session_state.rename_text = ""
                st.rerun()
            except Exception as e:
                st.error("Could not rename chat."); st.caption(str(e))
        else:
            st.warning("Enter a chat name first.")
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        try:
            delete_chat(st.session_state.current_chat_id)
            remaining = get_chats()
            if remaining:
                st.session_state.current_chat_id = remaining[0]["id"]
                st.session_state.messages = load_messages(remaining[0]["id"])
            else:
                new_id = create_chat()
                st.session_state.current_chat_id = new_id
                st.session_state.messages = []
            st.rerun()
        except Exception as e:
            st.error("Could not delete chat."); st.caption(str(e))

    st.markdown("---")
    st.markdown("### ✨ Features")
    st.markdown("""
    <div class="feature-card">💬 <b>Smart Conversations</b><br>Ask questions and get AI-powered answers.</div>
    <div class="feature-card">🧠 <b>Gemini AI</b><br>Powered by Google's Gemini model.</div>
    <div class="feature-card">🎤 <b>Voice Input</b><br>Speak your question instead of typing.</div>
    <div class="feature-card">☁️ <b>Cloud Chat Storage</b><br>Chat history is stored in Supabase.</div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🧹 Clear Current Chat", use_container_width=True):
        try:
            supabase.table("messages").delete().eq("chat_id", st.session_state.current_chat_id).execute()
            st.session_state.messages = []
            st.rerun()
        except Exception as e:
            st.error("Could not clear chat."); st.caption(str(e))
    st.markdown("---")
    st.caption("💡 Tip")
    st.caption("Ask me about Python, AI, ML, DBMS, web development, projects and more!")

# ---------------- MAIN ----------------
st.markdown('<div class="main-title">🤖 Gemini AI ChatBot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your friendly AI assistant powered by Gemini ✨</div>', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-card"><h2>👋 Hello! I'm your AI Assistant</h2>
    <p>Ask me anything and I'll try my best to help you.</p>
    <p>💻 Coding &nbsp; | &nbsp; 🤖 AI/ML &nbsp; | &nbsp; 📚 Study &nbsp; | &nbsp; 💡 Ideas</p></div>
    """, unsafe_allow_html=True)
    st.markdown("### 💡 Try asking")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🐍 Learn Python", use_container_width=True):
            st.session_state.pending_prompt = "Teach me Python from beginner level."; st.rerun()
        if st.button("🤖 What is AI?", use_container_width=True):
            st.session_state.pending_prompt = "Explain Artificial Intelligence in simple words."; st.rerun()
    with col2:
        if st.button("📊 Learn Machine Learning", use_container_width=True):
            st.session_state.pending_prompt = "Explain Machine Learning with a simple example."; st.rerun()
        if st.button("💡 Project Ideas", use_container_width=True):
            st.session_state.pending_prompt = "Give me some beginner-friendly AI and ML project ideas."; st.rerun()

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👩‍💻"): st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"): st.markdown(message["content"])

# ---------------- INPUTS ----------------
st.markdown("### 🎤 Voice Input")
audio_value = st.audio_input("Record your question", sample_rate=16000)
typed_prompt = st.chat_input("💬 Type your message here...")
prompt = typed_prompt
if not prompt and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if not prompt and audio_value is not None:
    with st.spinner("🎤 Converting your voice to text..."):
        try:
            voice_part = types.Part.from_bytes(data=audio_value.getvalue(), mime_type="audio/wav")
            voice_response = gemini_client.models.generate_content(
                model=MODEL_NAME,
                contents=[types.Content(role="user", parts=[
                    voice_part,
                    types.Part.from_text(text="Transcribe the spoken audio exactly as a user question. Return only the transcription, with no explanation or extra text. Preserve the language spoken by the user.")
                ])]
            )
            prompt = (voice_response.text or "").strip()
            if not prompt:
                st.warning("I couldn't understand the audio. Please try again.")
                st.stop()
        except Exception as e:
            st.error("❌ Voice processing failed."); st.caption(f"Error details: {e}"); st.stop()

# ---------------- CHAT PROCESSING ----------------
if prompt:
    prompt = prompt.strip()
    if not prompt: st.stop()
    st.session_state.messages.append({"role":"user","content":prompt})
    try:
        save_message(st.session_state.current_chat_id, "user", prompt)
    except Exception as e:
        st.error("❌ Could not save your message to Supabase."); st.caption(f"Error details: {e}")
    with st.chat_message("user", avatar="👩‍💻"): st.markdown(prompt)

    try:
        chats = get_chats()
        current_chat = next((c for c in chats if c["id"] == st.session_state.current_chat_id), None)
        if current_chat and current_chat.get("title") == "New Chat":
            title = prompt[:45].strip() + ("..." if len(prompt) > 45 else "")
            rename_chat(st.session_state.current_chat_id, title)
    except Exception:
        pass

    conversation = []
    for message in st.session_state.messages:
        conversation.append({"role": "model" if message["role"] == "assistant" else "user", "parts": [{"text": message["content"]}]})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("✨ Gemini is thinking..."):
            try:
                response = gemini_client.models.generate_content(model=MODEL_NAME, contents=conversation)
                answer = (response.text or "").strip() or "I couldn't generate a response. Please try again."
                st.markdown(answer)
                st.session_state.messages.append({"role":"assistant","content":answer})
                try:
                    save_message(st.session_state.current_chat_id, "assistant", answer)
                except Exception as e:
                    st.warning("Response was generated, but could not be saved to Supabase.")
                    st.caption(f"Save error: {e}")
            except Exception as e:
                st.error("❌ Something went wrong while connecting to Gemini.")
                st.caption(f"Error details: {e}")
