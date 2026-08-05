import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
}


def firebase_login_page():

    st.markdown(
        """
        <style>
        .login-card {
            max-width:430px;
            margin:60px auto;
            padding:35px;
            text-align:center;
            background:#1A0033;
            border:1px solid #5A189A;
            border-radius:16px;
            color:white;
        }

        .login-title {
            font-size:32px;
            font-weight:700;
        }

        .login-text {
            color:#C8B8DB;
            margin-bottom:25px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="login-card">

        <div class="login-title">
        🛡️ FraudShield AI
        </div>

        <br>

        <div class="login-text">
        Sign in securely with your Google account.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    login_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?client_id="
        + os.getenv("GOOGLE_CLIENT_ID", "")
        + "&redirect_uri="
        + os.getenv("GOOGLE_REDIRECT_URI", "")
        + "&response_type=id_token"
        "&scope=email%20profile%20openid"
        "&nonce=firebase"
    )


    st.link_button(
        "Continue with Google",
        login_url,
        use_container_width=True,
    )


def render_login():

    missing = [
        key
        for key, value in FIREBASE_CONFIG.items()
        if not value
    ]

    if missing:
        st.error(
            "Missing Firebase configuration: "
            + ", ".join(missing)
        )
        st.stop()


    if "firebase_user" not in st.session_state:
        st.session_state["firebase_user"] = None


    firebase_login_page()


    return st.session_state.get(
        "firebase_user"
    )