"""
RAGbot - AI-Powered Document Q&A Chatbot
Premium UI with Mobile Responsiveness
"""
import streamlit as st
from datetime import datetime
import time
import re

from src.auth import (
    sign_in, sign_up, sign_out, 
    get_current_user, is_authenticated
)
from src.document_processor import process_document
from src.vector_store import get_vector_store
from src.rag_chain import get_rag_chain
from src.chat_history import ChatHistory

# Page configuration
st.set_page_config(
    page_title="RAGbot - Document Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS with Mobile Responsiveness
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-tertiary: #1a1a25;
        --bg-card: rgba(255, 255, 255, 0.03);
        --border-color: rgba(255, 255, 255, 0.08);
        --text-primary: #f0f0f5;
        --text-secondary: #a0a0b0;
        --text-muted: #606070;
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        --success-color: #10b981;
        --error-color: #ef4444;
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Dark Background */
    .stApp {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    }
    
    /* Main Header */
    .main-header {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 700;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        color: var(--text-secondary);
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* ===== CHAT INTERFACE ===== */
    .chat-wrapper {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Message Container */
    .msg-container {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .msg-container.user {
        flex-direction: row-reverse;
    }
    
    /* Avatar */
    .msg-avatar {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    
    .msg-avatar.user {
        background: var(--accent-gradient);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .msg-avatar.bot {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Message Bubble */
    .msg-bubble {
        padding: 14px 18px;
        border-radius: 16px;
        max-width: 75%;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    @media (max-width: 768px) {
        .msg-bubble {
            max-width: 85%;
            padding: 12px 14px;
            font-size: 0.9rem;
        }
    }
    
    .msg-bubble.user {
        background: var(--accent-gradient);
        color: white;
        border-bottom-right-radius: 4px;
        margin-left: auto;
    }
    
    .msg-bubble.bot {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        border-bottom-left-radius: 4px;
    }
    
    /* Message Content Wrapper */
    .msg-content {
        display: flex;
        flex-direction: column;
        max-width: calc(100% - 50px);
    }
    
    .msg-content.user {
        align-items: flex-end;
    }
    
    /* Timestamp */
    .msg-time {
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 6px;
        padding: 0 4px;
    }
    
    /* Sources Box */
    .sources-container {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 10px;
        max-width: 75%;
    }
    
    @media (max-width: 768px) {
        .sources-container {
            max-width: 85%;
        }
    }
    
    .sources-label {
        font-size: 0.7rem;
        color: var(--success-color);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    
    .source-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 2px 4px 2px 0;
    }
    
    /* Typing Indicator */
    .typing-wrapper {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .typing-bubble {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        padding: 16px 24px;
        border-radius: 16px;
        border-bottom-left-radius: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: var(--accent-primary);
        border-radius: 50%;
        animation: typingBounce 1.4s ease-in-out infinite;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-8px); opacity: 1; }
    }
    
    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    
    /* Sidebar Buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--bg-card);
        border-color: var(--accent-primary);
        transform: translateY(-1px);
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: var(--accent-gradient);
        border: none;
        color: white;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* User Card */
    .user-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .user-avatar {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: var(--accent-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    .user-info {
        flex: 1;
        overflow: hidden;
    }
    
    .user-name {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.95rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .user-email {
        color: var(--text-muted);
        font-size: 0.75rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Session Card */
    .session-item {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .session-item:hover {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .session-item.active {
        background: rgba(99, 102, 241, 0.12);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .session-title {
        color: var(--text-primary);
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .session-meta {
        color: var(--text-muted);
        font-size: 0.7rem;
        display: flex;
        gap: 8px;
    }
    
    /* Document Card */
    .doc-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    
    .doc-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .doc-icon {
        font-size: 1.5rem;
        margin-bottom: 6px;
    }
    
    .doc-name {
        color: var(--text-primary);
        font-size: 0.85rem;
        font-weight: 500;
        word-break: break-word;
    }
    
    .doc-meta {
        color: var(--text-muted);
        font-size: 0.7rem;
        margin-top: 4px;
    }
    
    /* Stats Badge */
    .stats-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    
    .stat-badge {
        background: rgba(99, 102, 241, 0.1);
        color: var(--accent-primary);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Search Box */
    .search-box {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
    }
    
    .search-box:focus-within {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .search-icon {
        color: var(--text-muted);
        font-size: 0.9rem;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--text-secondary);
    }
    
    .empty-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        opacity: 0.6;
    }
    
    .empty-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .empty-desc {
        font-size: 0.9rem;
        color: var(--text-muted);
        max-width: 300px;
        margin: 0 auto;
    }
    
    /* Progress Bar */
    .progress-container {
        background: var(--bg-tertiary);
        border-radius: 10px;
        height: 6px;
        overflow: hidden;
        margin: 12px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: var(--accent-gradient);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Action Buttons Row */
    .action-row {
        display: flex;
        gap: 8px;
        margin: 12px 0;
        flex-wrap: wrap;
    }
    
    .action-btn {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .action-btn:hover {
        background: var(--bg-card);
        color: var(--text-primary);
        border-color: var(--accent-primary);
    }
    
    /* Auth Card */
    .auth-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        max-width: 400px;
        margin: 0 auto;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    /* Hide Streamlit defaults but keep header for sidebar toggle */
    #MainMenu, footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Style the header to be minimal but keep toggle visible */
    header[data-testid="stHeader"] {
        background: transparent;
        backdrop-filter: none;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.5);
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        .msg-avatar {
            width: 32px;
            height: 32px;
            font-size: 0.9rem;
        }
        
        .msg-container {
            gap: 8px;
        }
        
        .user-card {
            padding: 10px;
        }
        
        .user-avatar {
            width: 36px;
            height: 36px;
        }
        
        .auth-card {
            padding: 1.5rem;
            margin: 0 1rem;
        }
        
        .empty-state {
            padding: 2rem 1rem;
        }
        
        .empty-icon {
            font-size: 2.5rem;
        }
    }
    
    /* Tablet */
    @media (max-width: 1024px) and (min-width: 769px) {
        .chat-wrapper {
            max-width: 700px;
        }
    }
    
    /* Section Headers */
    .section-header {
        color: var(--text-secondary);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
        padding-left: 4px;
    }
    
    /* Feature highlight */
    .feature-badge {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Add custom CSS for fixed sidebar and enhanced UI
st.markdown("""
<style>
    
    /* Optimize Sidebar for Mobile */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 85vw !important;
            max-width: 320px !important;
            min-width: 250px !important;
        }
        
        .user-card {
             padding: 10px;
        }
    }
    
    /* Enhanced Auth Card (Targeting Streamlit Form) */
    [data-testid="stForm"] {
        background: rgba(18, 18, 26, 0.7) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 
                    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    [data-testid="stForm"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 
                    0 0 0 1px rgba(99, 102, 241, 0.2) inset;
        border-color: rgba(99, 102, 241, 0.2);
    }
    
    /* Improve Input Fields */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
        padding-left: 12px !important;
    }
    
    .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Tab Styling in Auth */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 4px;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #a0a0b0;
        border-radius: 8px;
        padding: 8px 16px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        font-weight: 600;
    }
    
    /* Center the Auth Card better */
    .main-header {
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "user": None,
        "messages": [],
        "current_session_id": None,
        "is_streaming": False,
        "search_query": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def format_time(iso_string: str) -> str:
    """Format ISO timestamp to readable time"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%I:%M %p")
    except:
        return datetime.now().strftime("%I:%M %p")


def format_relative_date(iso_string: str) -> str:
    """Format ISO timestamp to relative date"""
    try:
        dt = datetime.fromisoformat(iso_string)
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            return "Today"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        else:
            return dt.strftime("%b %d")
    except:
        return ""


def render_auth_page():
    """Render modern login/signup page"""
    st.markdown('<h1 class="main-header">🤖 RAGbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI-Powered Document Assistant</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])
        
        with tab1:
            with st.form("signin_form", clear_on_submit=False):
                st.markdown("#### Welcome back!")
                email = st.text_input("Email", placeholder="you@example.com", key="si_email")
                password = st.text_input("Password", type="password", key="si_pass")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    remember = st.checkbox("Remember me", value=True)
                
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                
                if submit:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        with st.spinner("Signing in..."):
                            success, message, user_data = sign_in(email, password)
                        if success:
                            st.session_state.user = user_data
                            st.success("Welcome back! 🎉")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)
        
        with tab2:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("#### Get started for free")
                email = st.text_input("Email", placeholder="you@example.com", key="su_email")
                password = st.text_input("Password", type="password", key="su_pass", 
                                        help="At least 6 characters")
                confirm = st.text_input("Confirm Password", type="password", key="su_confirm")
                
                submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if submit:
                    if not email or not password or not confirm:
                        st.error("Please fill in all fields")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif password != confirm:
                        st.error("Passwords don't match")
                    else:
                        with st.spinner("Creating account..."):
                            success, message = sign_up(email, password)
                        if success:
                            st.success("Account created! Please sign in.")
                        else:
                            st.error(message)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">
                Upload documents • Ask questions • Get instant answers
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                <span class="stat-badge">📄 PDF, DOCX, TXT</span>
                <span class="stat-badge">⚡ Powered by Groq</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    """Render enhanced sidebar"""
    user = get_current_user()
    vector_store = get_vector_store()
    chat_history = ChatHistory(user_token=user["access_token"])
    
    with st.sidebar:
        # User Card
        username = user['email'].split('@')[0].title()
        st.markdown(f"""
        <div class="user-card">
            <div class="user-avatar">👤</div>
            <div class="user-info">
                <div class="user-name">{username}</div>
                <div class="user-email">{user['email']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Logout", use_container_width=True):
                sign_out()
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col2:
            if st.button("✨ New Chat", use_container_width=True, type="primary"):
                session = chat_history.create_session(user["id"])
                st.session_state.current_session_id = session["id"]
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("---")
        
        # Chat Sessions
        st.markdown('<div class="section-header">💬 Conversations</div>', unsafe_allow_html=True)
        
        sessions = chat_history.list_sessions(user["id"])
        
        if sessions:
            for session in sessions[:8]:
                is_active = session["id"] == st.session_state.current_session_id
                icon = "📌" if is_active else "💬"
                
                col1, col2 = st.columns([6, 1])
                with col1:
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(
                        f"{icon} {session['title'][:28]}{'...' if len(session['title']) > 28 else ''}",
                        key=f"sess_{session['id']}",
                        use_container_width=True,
                        type=btn_type
                    ):
                        full_session = chat_history.get_session(user["id"], session["id"])
                        if full_session:
                            st.session_state.current_session_id = session["id"]
                            st.session_state.messages = full_session.get("messages", [])
                            st.rerun()
                
                with col2:
                    if st.button("×", key=f"del_{session['id']}", help="Delete"):
                        chat_history.delete_session(user["id"], session["id"])
                        if session["id"] == st.session_state.current_session_id:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: var(--text-muted);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💬</div>
                <div style="font-size: 0.8rem;">No conversations yet</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Documents Section
        st.markdown('<div class="section-header">📁 Documents</div>', unsafe_allow_html=True)
        
        # Document Search
        search = st.text_input(
            "Search documents",
            placeholder="🔍 Search...",
            key="doc_search",
            label_visibility="collapsed"
        )
        
        # File Upload
        uploaded_files = st.file_uploader(
            "Upload",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="Drag and drop files here"
        )
        
        if uploaded_files:
            if st.button("📥 Process Files", use_container_width=True, type="primary"):
                progress = st.progress(0)
                status = st.empty()
                
                for i, file in enumerate(uploaded_files):
                    status.markdown(f"⏳ Processing **{file.name}**...")
                    progress.progress((i) / len(uploaded_files))
                    
                    try:
                        chunks = process_document(file)
                        num_chunks = vector_store.add_documents(chunks, user["id"])
                        status.markdown(f"✅ **{file.name}** - {num_chunks} chunks")
                    except Exception as e:
                        st.error(f"❌ {file.name}: {str(e)}")
                    
                    progress.progress((i + 1) / len(uploaded_files))
                
                time.sleep(0.5)
                st.rerun()
        
        # Document List
        documents = vector_store.get_document_list(user["id"])
        
        # Filter by search
        if search:
            documents = [d for d in documents if search.lower() in d.lower()]
        
        if documents:
            for doc in documents[:10]:
                ext = doc.split('.')[-1].upper() if '.' in doc else 'TXT'
                icon = "📄" if ext == "TXT" else "📕" if ext == "PDF" else "📘"
                
                with st.expander(f"{icon} {doc[:22]}{'...' if len(doc) > 22 else ''}", expanded=False):
                    st.markdown(f"**{doc}**")
                    st.markdown(f"<span class='feature-badge'>{ext}</span>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"deldoc_{doc}", use_container_width=True):
                        vector_store.delete_document(user["id"], doc)
                        st.rerun()
        elif not search:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: var(--text-muted);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📁</div>
                <div style="font-size: 0.8rem;">No documents uploaded</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Stats
        st.markdown("---")
        chunk_count = vector_store.get_document_count(user["id"])
        st.markdown(f"""
        <div class="stats-row">
            <span class="stat-badge">📚 {len(vector_store.get_document_list(user["id"]))} docs</span>
            <span class="stat-badge">🧩 {chunk_count} chunks</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Clear All
        if documents:
            st.markdown("")
            if st.button("🗑️ Clear All Data", use_container_width=True):
                vector_store.clear_user_data(user["id"])
                chat_history.clear_all_sessions(user["id"])
                st.session_state.messages = []
                st.session_state.current_session_id = None
                st.rerun()


def render_message(role: str, content: str, sources: list = None, timestamp: str = None):
    """Render a single chat message"""
    time_str = format_time(timestamp) if timestamp else datetime.now().strftime("%I:%M %p")
    
    # Clean the content - remove any accidentally stored HTML
    clean_content = content
    # Remove any previously rendered HTML that might have been stored
    if '<div class="sources-container">' in clean_content:
        clean_content = clean_content.split('<div class="sources-container">')[0]
    if '<div class="msg-' in clean_content:
        # Content has HTML from previous render, extract just text
        import re
        clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Escape HTML in content but preserve line breaks
    safe_content = clean_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_content = safe_content.replace("\n", "<br>")
    
    if role == "user":
        st.markdown(f"""
        <div class="msg-container user">
            <div class="msg-avatar user">👤</div>
            <div class="msg-content user">
                <div class="msg-bubble user">{safe_content}</div>
                <div class="msg-time">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Build sources section separately using Streamlit components
        st.markdown(f"""
        <div class="msg-container">
            <div class="msg-avatar bot">🤖</div>
            <div class="msg-content">
                <div class="msg-bubble bot">{safe_content}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Render sources with proper Streamlit expander for reliability
        if sources and len(sources) > 0:
            with st.expander("📚 Sources", expanded=False):
                for source in sources[:5]:
                    st.markdown(f"• **{source}**")
        
        st.markdown(f'<div class="msg-time" style="padding-left: 50px;">{time_str}</div>', unsafe_allow_html=True)


def render_typing():
    """Render typing indicator"""
    st.markdown("""
    <div class="typing-wrapper">
        <div class="msg-avatar bot">🤖</div>
        <div class="typing-bubble">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat():
    """Render main chat interface"""
    user = get_current_user()
    chat_history = ChatHistory(user_token=user["access_token"])
    
    # Ensure session exists
    if not st.session_state.current_session_id:
        sessions = chat_history.list_sessions(user["id"])
        if sessions:
            latest = sessions[0]
            full_session = chat_history.get_session(user["id"], latest["id"])
            st.session_state.current_session_id = latest["id"]
            st.session_state.messages = full_session.get("messages", []) if full_session else []
        else:
            session = chat_history.create_session(user["id"])
            st.session_state.current_session_id = session["id"]
    
    # Header
    st.markdown('<h1 class="main-header">🤖 RAGbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask anything about your documents</p>', unsafe_allow_html=True)
    
    # Action buttons
    if st.session_state.messages:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            export_md = chat_history.export_session(
                user["id"], 
                st.session_state.current_session_id, 
                "markdown"
            )
            st.download_button(
                "📥 Export",
                export_md,
                file_name=f"chat_{st.session_state.current_session_id}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Chat Container
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">💬</div>
                <div class="empty-title">Start a conversation</div>
                <div class="empty-desc">
                    Upload documents using the sidebar, then ask questions about them.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                render_message(
                    msg["role"],
                    msg["content"],
                    msg.get("sources", []),
                    msg.get("timestamp")
                )
    
    # Chat Input
    if prompt := st.chat_input("Ask a question about your documents..."):
        timestamp = datetime.now().isoformat()
        
        # Add user message
        user_msg = {
            "role": "user",
            "content": prompt,
            "timestamp": timestamp,
            "sources": []
        }
        st.session_state.messages.append(user_msg)
        
        chat_history.add_message(
            user["id"],
            st.session_state.current_session_id,
            "user",
            prompt
        )
        
        # Display user message
        with chat_container:
            render_message("user", prompt, timestamp=timestamp)
        
        # Generate response with streaming
        response_area = st.empty()
        
        with response_area.container():
            render_typing()
        
        try:
            rag_chain = get_rag_chain()
            
            # Use streaming
            full_response = ""
            sources = []
            
            # Prepare history for context (exclude current user message which is already in prompt)
            # We want the conversation *before* this question
            history = st.session_state.messages[:-1] 
            
            for chunk in rag_chain.get_response_stream(prompt, user["id"], history):
                if chunk["type"] == "chunk":
                    full_response += chunk["content"]
                    # Update display with partial response
                    with response_area.container():
                        render_message("assistant", full_response + "▌", [], timestamp=datetime.now().isoformat())
                
                elif chunk["type"] == "complete":
                    full_response = chunk["response"]
                    sources = chunk["sources"]
                
                elif chunk["type"] == "error":
                    full_response = f"Sorry, I encountered an error: {chunk['error']}"
            
            # Final display
            response_area.empty()
            
            response_timestamp = datetime.now().isoformat()
            
            # Save to state and history
            assistant_msg = {
                "role": "assistant",
                "content": full_response,
                "sources": sources,
                "timestamp": response_timestamp
            }
            st.session_state.messages.append(assistant_msg)
            
            chat_history.add_message(
                user["id"],
                st.session_state.current_session_id,
                "assistant",
                full_response,
                sources
            )
            
            st.rerun()
            
        except Exception as e:
            response_area.empty()
            error_msg = f"Sorry, something went wrong: {str(e)}"
            st.error(error_msg)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "sources": [],
                "timestamp": datetime.now().isoformat()
            })


def main():
    """Main entry point"""
    init_session_state()
    
    if is_authenticated():
        render_sidebar()
        render_chat()
    else:
        render_auth_page()


if __name__ == "__main__":
    main()
