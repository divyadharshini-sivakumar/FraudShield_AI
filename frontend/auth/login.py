import json
import os

import streamlit as st
import streamlit.components.v1 as components
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


    components.html(
        f"""
        <script type="module">

        import {{
            initializeApp
        }} from
        "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";


        import {{
            getAuth,
            GoogleAuthProvider,
            signInWithPopup
        }} from
        "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";


        const config = {json.dumps(FIREBASE_CONFIG)};


        const app = initializeApp(config);

        const auth = getAuth(app);

        const provider = new GoogleAuthProvider();


        document.body.innerHTML = `

        <div style="
            text-align:center;
            padding:40px;
            color:white;
        ">

        <h2>
        🛡️ FraudShield AI
        </h2>

        <p>
        Sign in securely with your Google account.
        </p>


        <button id="google-login"
        style="
        padding:14px 40px;
        border-radius:8px;
        border:none;
        background:#7B2CBF;
        color:white;
        font-size:16px;
        cursor:pointer;
        ">
        Continue with Google
        </button>


        <p id="status"></p>

        </div>

        `;


        document
        .getElementById("google-login")
        .onclick = async () => {{

            const status =
            document.getElementById("status");


            try {{

                status.innerHTML =
                "Signing in...";


                const result =
                await signInWithPopup(
                    auth,
                    provider
                );


                const token =
                await result.user.getIdToken();


                localStorage.setItem(
                    "firebase_user",
                    JSON.stringify({{
                        uid: result.user.uid,
                        email: result.user.email,
                        name: result.user.displayName,
                        id_token: token
                    }})
                );


                window.parent.location.reload();


            }} catch(error) {{

                status.innerHTML =
                error.message;

            }}

        }};

        </script>
        """,
        height=300,
    )


    return st.session_state.get(
        "firebase_user"
    )