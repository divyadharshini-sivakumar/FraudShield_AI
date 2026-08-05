import streamlit as st
import sys
import os
import requests
from dotenv import load_dotenv
import streamlit.components.v1 as components

def receive_firebase_login():
    components.html(
        """
        <script>
        window.addEventListener("message", (event) => {
            if (event.data.type === "firebase_login") {
                window.parent.postMessage(
                    {
                        type: "streamlit:setComponentValue",
                        value: event.data.user
                    },
                    "*"
                );
            }
        });
        </script>
        """,
        height=0,
    )
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env
load_dotenv()

st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Apply Dark Purple/Blue Theme CSS — comprehensive
st.markdown("""
    <style>
    /* === ROOT VARS === */
    :root {
        --primary: #9D4EDD;
        --primary-dark: #7B2CBF;
        --bg-main: #0D001A;
        --bg-card: rgba(60, 9, 108, 0.25);
        --bg-input: #1A0033;
        --border: #5A189A;
        --text-main: #F0E6FF;
        --text-secondary: #C8B8DB;
        --text-bright: #FFFFFF;
        --accent-green: #00E396;
        --accent-red: #FF4560;
    }

    /* === APP BACKGROUND === */
    .stApp {
        background: linear-gradient(135deg, #0D001A 0%, #10002B 50%, #1A0033 100%);
        color: var(--text-main);
    }

    /* === HEADINGS === */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-bright) !important;
    }

    /* === ALL TEXT / PARAGRAPHS === */
    p, span, label, .stMarkdown, .stText, 
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: var(--text-main) !important;
    }

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10002B, #1A0033) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-main) !important;
    }

    /* === INPUTS, SELECTS, TEXT AREAS === */
    input, textarea, select,
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] div {
        background-color: var(--bg-input) !important;
        color: var(--text-bright) !important;
        border-color: var(--border) !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background-color: var(--bg-input) !important;
        color: var(--text-bright) !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] div[role="option"],
    .stMultiSelect span {
        color: var(--text-bright) !important;
    }

    /* === DROPDOWN MENUS === */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #1A0033 !important;
    }
    ul[role="listbox"] li,
    [data-baseweb="menu"] li {
        color: var(--text-bright) !important;
    }
    ul[role="listbox"] li:hover,
    [data-baseweb="menu"] li:hover {
        background-color: var(--primary-dark) !important;
    }

    /* === METRIC CARDS === */
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: var(--text-bright) !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-bright) !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    /* === BUTTONS === */
    .stButton > button,
    button[kind="primary"],
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
        color: var(--text-bright) !important;
        border: 1px solid var(--border) !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, var(--primary), #B75CFF) !important;
    }

    /* === DATAFRAMES / TABLES === */
    [data-testid="stDataFrame"], .stDataFrame {
        background-color: var(--bg-card) !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: #2D0059 !important;
        color: var(--text-bright) !important;
    }
    [data-testid="stDataFrame"] td {
        color: var(--text-main) !important;
    }

    /* === CHAT MESSAGES === */
    [data-testid="stChatMessage"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span {
        color: var(--text-main) !important;
    }

    /* === EXPANDERS === */
    details, .streamlit-expanderHeader {
        background-color: var(--bg-card) !important;
        color: var(--text-main) !important;
        border-color: var(--border) !important;
    }

    /* === ALERTS / CALLOUTS === */
    [data-testid="stAlert"] {
        color: var(--text-bright) !important;
    }

    /* === RADIO BUTTONS === */
    .stRadio label span,
    .stCheckbox label span {
        color: var(--text-main) !important;
    }

    /* === CAPTION === */
    .stCaption, [data-testid="stCaption"] {
        color: var(--text-secondary) !important;
    }

    /* === FORM === */
    [data-testid="stForm"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
    }

    /* === CUSTOM CARDS === */
    .metric-card {
        background-color: var(--bg-card);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid var(--border);
    }
    .fraud-label { color: var(--accent-red); font-weight: bold; font-size: 24px; }
    .genuine-label { color: var(--accent-green); font-weight: bold; font-size: 24px; }
    /* Hide Streamlit default UI */
    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    button[kind="header"] {
        display: none !important;
    }

    /* Sidebar radio styling */
    .stRadio > div {
        gap: 8px;
    }

    .stRadio label {
        padding: 8px;
        border-radius: 8px;
    }

    .stRadio label:hover {
        background: rgba(157, 78, 221, 0.15);
    }

    [data-testid="collapsedControl"]{
    display:none !important;
    }

    /* Hide default Streamlit multipage navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    [data-testid="stSidebarNavItems"] {
        display: none !important;
    }

    [data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }

    [data-testid="stSidebarNavViewButton"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] ul:first-of-type {
        display: none !important;
    }

    /* ===== SELECTBOX FIELD ===== */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #1A0033 !important;
        border-color: #5A189A !important;
        color: #FFFFFF !important;
    }

    /* Selected value and placeholder */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #FFFFFF !important;
    }

    /* Arrow area */
    .stSelectbox [data-baseweb="select"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Remove the white arrow box */
    .stSelectbox [data-baseweb="select"] > div > div:last-child {
        background-color: #1A0033 !important;
    }

    /* ===== OPEN DROPDOWN MENU ===== */
    [data-baseweb="popover"] {
        background-color: transparent !important;
    }

    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul[role="listbox"] {
        background-color: #1A0033 !important;
        border: 1px solid #5A189A !important;
    }

    /* Dropdown options */
    [data-baseweb="popover"] li[role="option"] {
        background-color: #1A0033 !important;
        color: #FFFFFF !important;
    }

    /* Everything inside each option */
    [data-baseweb="popover"] li[role="option"] * {
        color: #FFFFFF !important;
    }

    /* Hovered option */
    [data-baseweb="popover"] li[role="option"]:hover {
        background-color: #5A189A !important;
    }

    /* Selected/highlighted option */
    [data-baseweb="popover"] li[role="option"][aria-selected="true"] {
        background-color: #7B2CBF !important;
        color: #FFFFFF !important;
    }
    /* Fix number input stepper buttons */
    [data-testid="stNumberInput"] button {
        background-color: #1A0033 !important;
        color: #FFFFFF !important;
        border-left: 1px solid #5A189A !important;
    }

    [data-testid="stNumberInput"] button:hover {
        background-color: #5A189A !important;
        color: #FFFFFF !important;
    }

    [data-testid="stNumberInput"] button svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Keep the complete number input dark */
    [data-testid="stNumberInput"] > div > div {
        background-color: #1A0033 !important;
        border-color: #5A189A !important;
    }

    [data-testid="stNumberInput"] input {
        background-color: #1A0033 !important;
        color: #FFFFFF !important;
    }

    /* Make placeholders readable */
    [data-testid="stNumberInput"] input::placeholder,
    .stTextInput input::placeholder {
        color: #BFA8D8 !important;
        opacity: 1 !important;
    }

    button[data-baseweb="button"] {
        background-color: #1A0033 !important;
        color: #FFFFFF !important;
    }

    button[data-baseweb="button"]:hover {
        background-color: #5A189A !important;
    }

    /* ===== Code Blocks ===== */
    pre,
    code,
    .stCodeBlock,
    [data-testid="stCodeBlock"] {
        background: #18002f !important;
        color: #F8F8F2 !important;
    }

    [data-testid="stCodeBlock"] pre {
        background: #18002f !important;
        color: #F8F8F2 !important;
    }

    [data-testid="stCode"] {
        background: #18002f !important;
    }

    .hljs {
        background: #18002f !important;
        color: #F8F8F2 !important;
    }

    .hljs-string {
        color: #7CFC92 !important;
    }

    .hljs-number {
        color: #FFB86C !important;
    }

    .hljs-attr,
    .hljs-keyword {
        color: #8BE9FD !important;
    }

    .hljs-literal {
        color: #FF79C6 !important;
    }

    /* Read-only JSON text area */
    [data-testid="stTextArea"] textarea {
        background-color: #140026 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
        caret-color: #FFFFFF !important;
    }

    [data-testid="stTextArea"] textarea:disabled {
        background-color: #140026 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
    }

    [data-testid="stTextArea"] textarea::selection {
        background-color: #7B2CBF !important;
        color: #FFFFFF !important;
    }

    /* Hide Streamlit's automatic pages list */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"],
    [data-testid="stSidebarNavViewButton"] {
        display: none !important;
    }

    /* Hide the full sidebar on the login page */
    body:has(.firebase-login-marker) section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Hide the sidebar open/collapse button on the login page */
    body:has(.firebase-login-marker) [data-testid="collapsedControl"],
    body:has(.firebase-login-marker) [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Center the login page */
    body:has(.firebase-login-marker) .block-container {
        max-width: 760px !important;
        padding-top: 7rem !important;
    }

    /* Placeholder text inside Selectbox */
    .stSelectbox div[data-baseweb="select"] > div {
        color: #FFFFFF !important;
    }

    /* Selected value */
    .stSelectbox span {
        color: #FFFFFF !important;
    }

    /* Placeholder */
    .stSelectbox input::placeholder {
        color: #CFCFCF !important;
        opacity: 1 !important;
    }

    /* Dropdown arrow */
    .stSelectbox svg {
        fill: white !important;
    }

    /* ===== CHATBOT PAGE ===== */

    .chatbot-header {
        margin-bottom: 14px;
    }

    .chatbot-header h1 {
        font-size: 38px;
        margin-bottom: 6px;
        color: #FFFFFF !important;
    }

    .chatbot-header p {
        color: #C8B8DB !important;
        font-size: 15px;
        margin: 0;
    }

    .chatbot-status {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 9px 14px;
        margin: 8px 0 24px 0;
        border-radius: 9px;
        border: 1px solid #5A189A;
        background: rgba(60, 9, 108, 0.28);
        color: #FFFFFF !important;
        font-size: 13px;
    }

    .chatbot-status span {
        color: #C8B8DB !important;
        font-size: 12px;
    }

    .chatbot-welcome {
        max-width: 680px;
        margin: 60px auto 20px auto;
        padding: 30px;
        text-align: center;
        border: 1px solid #5A189A;
        border-radius: 16px;
        background: rgba(60, 9, 108, 0.22);
    }

    .chatbot-welcome h3 {
        color: #FFFFFF !important;
        margin-bottom: 10px;
    }

    .chatbot-welcome p {
        color: #C8B8DB !important;
        margin: 0;
        line-height: 1.6;
    }

    /* Chat message cards */
    [data-testid="stChatMessage"] {
        background: rgba(60, 9, 108, 0.26) !important;
        border: 1px solid #5A189A !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatMessage"] p {
        color: #F0E6FF !important;
        line-height: 1.6 !important;
    }

    /* Chat input outer container */
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
    }

    /* Chat input wrapper */
    [data-testid="stChatInput"] > div {
        background: #1A0033 !important;
        border: 1px solid #5A189A !important;
        border-radius: 14px !important;
    }

    /* Chat input text */
    [data-testid="stChatInput"] textarea {
        background: #1A0033 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: none !important;
    }

    /* Chat input placeholder */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #BFA8D8 !important;
        opacity: 1 !important;
    }

    /* Send button */
    [data-testid="stChatInput"] button {
        background: #7B2CBF !important;
        color: #FFFFFF !important;
        border-radius: 9px !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: #9D4EDD !important;
    }

    /* Remove white footer area around chat input */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"] {
        background: #0D001A !important;
    }
    </style>
""", unsafe_allow_html=True)



firebase_user = {
    "name": "DIVYA DHARSHINI S",
    "email": "admin@fraudshield.ai"
}

if not isinstance(firebase_user, dict):
    st.session_state.pop("firebase_user", None)
    user = render_login()

    if not user:
        st.stop()

    firebase_user = user


if "app_user" not in st.session_state:
    st.session_state["app_user"] = {
        "name": "DIVYA DHARSHINI S",
        "email": "admin@fraudshield.ai",
        "role": "admin"
    }

user_name = (
    firebase_user.get("name")
    or firebase_user.get("email")
    or "User"
)
user_email = (
    firebase_user.get("email")
    or ""
).strip().lower()

admin_emails = {
    email.strip().lower()
    for email in os.getenv(
        "FIREBASE_ADMIN_EMAILS",
        "",
    ).split(",")
    if email.strip()
}

app_user = st.session_state.get("app_user", {})


user_name = app_user.get("name") or firebase_user.get("name") or "User"
user_email = app_user.get("email") or firebase_user.get("email") or ""

st.session_state["user_role"] = user_role

# Sidebar
st.sidebar.markdown("""
<div style="text-align:center;padding-bottom:15px;">
<h1 style="color:white;margin-bottom:0;">🛡 FraudShield AI</h1>
<p style="color:#c8b8db;margin-top:0;">
Real-Time Fraud Detection Platform
</p>
</div>
""", unsafe_allow_html=True)



FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://127.0.0.1:8000")
try:
    res = requests.get(f"{FASTAPI_BASE_URL}/api/health", timeout=3)
    if res.status_code == 200:
        health = res.json()
        if health.get("status") == "ok":
            pass
            
        else:
            st.sidebar.warning("🟡 API responded but status is not ok")
    else:
        st.sidebar.error("🔴 System Offline")
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔴 System Offline")
except requests.exceptions.Timeout:
    st.sidebar.error("🔴 System Offline")
except Exception:
    st.sidebar.error("🔴 System Offline")

st.sidebar.markdown("---")

if user_role == "admin":
    page_options = [
        "📊 Dashboard",
        "🔍 Prediction",
        "📑 Reports",
        "🤖 Chatbot",
        "⚙️ Train Model",
    ]
else:
    page_options = [
        "🔍 Prediction",
        "🤖 Chatbot",
    ]

page = st.sidebar.radio(
    "",
    page_options,
)

if page == "📊 Dashboard":
    from frontend.pages.dashboard import render_dashboard
    render_dashboard()
elif page == "🔍 Prediction":
    from frontend.pages.predict import render_predict
    render_predict()
elif page == "📑 Reports":
    from frontend.pages.reports import render_reports
    render_reports()
elif page == "🤖 Chatbot":
    from frontend.pages.chatbot import render_chatbot
    render_chatbot()
elif page == "⚙️ Train Model":
    from frontend.pages.train import render_train
    render_train()
