import os

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


LOGIN_HTML = """
<div class="login-card">
    <h2>FraudShield AI</h2>
    <p>Sign in securely with your Google account.</p>

    <button id="google-login">
        Continue with Google
    </button>

    <p id="login-status"></p>
</div>
"""


LOGIN_CSS = """
.login-card {
    max-width: 430px;
    margin: 25px auto;
    padding: 34px;
    text-align: center;
    background: rgba(60, 9, 108, 0.28);
    border: 1px solid #5A189A;
    border-radius: 14px;
    color: #FFFFFF;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
}

.login-card h2 {
    color: #FFFFFF;
    font-size: 30px;
    margin: 0 0 12px 0;
}

.login-card p {
    color: #C8B8DB;
    margin-bottom: 22px;
}

#google-login {
    width: 100%;
    padding: 13px 20px;
    border: 1px solid #5A189A;
    border-radius: 8px;
    background: linear-gradient(135deg, #7B2CBF, #9D4EDD);
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
}

#google-login:hover {
    background: linear-gradient(135deg, #9D4EDD, #B75CFF);
}

#google-login:disabled {
    opacity: 0.65;
    cursor: not-allowed;
}

#login-status {
    margin-top: 16px;
    color: #C8B8DB;
}
"""


LOGIN_JS = """
export default function(component) {
    const {
        data,
        setTriggerValue,
        parentElement
    } = component;

    const firebaseConfig = data.firebaseConfig;

    const status = parentElement.querySelector("#login-status");
    const button = parentElement.querySelector("#google-login");

    async function loadFirebase() {
        const appModule = await import(
            "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js"
        );

        const authModule = await import(
            "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js"
        );

        return {
            appModule,
            authModule
        };
    }

    button.onclick = async () => {
        try {
            button.disabled = true;
            status.textContent = "Signing in...";

            const {
                appModule,
                authModule
            } = await loadFirebase();

            const app = appModule.getApps().length
                ? appModule.getApp()
                : appModule.initializeApp(firebaseConfig);

            const auth = authModule.getAuth(app);
            const provider = new authModule.GoogleAuthProvider();

            const result = await authModule.signInWithPopup(
                auth,
                provider
            );

            const user = result.user;
            const idToken = await user.getIdToken(true);

            setTriggerValue("auth_result", {
                uid: user.uid,
                email: user.email,
                name: user.displayName,
                photo_url: user.photoURL,
                id_token: idToken
            });

            status.textContent = "Signed in successfully.";

        } catch (error) {
            status.textContent =
                "Login failed: " + error.message;

        } finally {
            button.disabled = false;
        }
    };
}
"""


google_login_component = st.components.v2.component(
    "fraudshield_google_login",
    html=LOGIN_HTML,
    css=LOGIN_CSS,
    js=LOGIN_JS,
)


def render_login():
    st.markdown(
        '<div class="firebase-login-marker"></div>',
        unsafe_allow_html=True,
    )

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

    result = google_login_component(
        data={
            "firebaseConfig": FIREBASE_CONFIG,
        },
        key="firebase_google_login",
        on_auth_result_change=lambda: None,
    )

    auth_result = getattr(
        result,
        "auth_result",
        None,
    )

    if auth_result:
        st.session_state["firebase_user"] = auth_result
        st.rerun()

    return st.session_state.get("firebase_user")