import os

import streamlit as st
import streamlit.components.v1 as components
import json
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

    firebase_config_json = json.dumps(
        FIREBASE_CONFIG
    )

    components.html(
        f"""
        <style>
        {LOGIN_CSS}
        </style>

        <div class="login-card">
            <h2>FraudShield AI</h2>
            <p>Sign in securely with your Google account.</p>

            <button id="google-login">
                Continue with Google
            </button>

            <p id="login-status"></p>
        </div>

        <script type="module">

        import {{
            initializeApp
        }} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";

        import {{
            getAuth,
            GoogleAuthProvider,
            signInWithPopup
        }} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";


        const firebaseConfig = {firebase_config_json};

        const app = initializeApp(firebaseConfig);

        const auth = getAuth(app);

        const provider = new GoogleAuthProvider();


        document
        .getElementById("google-login")
        .onclick = async () => {{

            const result =
                await signInWithPopup(
                    auth,
                    provider
                );

            const token =
                await result.user.getIdToken();


            window.parent.postMessage(
                {{
                    type: "firebase_login",
                    user: {{
                        uid: result.user.uid,
                        email: result.user.email,
                        name: result.user.displayName,
                        id_token: token
                    }}
                }},
                "*"
            );
        }}

        </script>
        """,
        height=350,
    )