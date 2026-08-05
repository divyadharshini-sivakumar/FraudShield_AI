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
    st.write(FIREBASE_CONFIG)

    components.html(
        f"""
        <script type="module">

        import {{ initializeApp }}
        from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";

        import {{
            getAuth,
            GoogleAuthProvider,
            signInWithRedirect,
            getRedirectResult
        }}
        from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";


        const config = {firebase_config_json};

        const app = initializeApp(config);

        const auth = getAuth(app);

        const provider = new GoogleAuthProvider();
        const redirectResult = await getRedirectResult(auth);

        if (redirectResult) {{
            const token = await redirectResult.user.getIdToken();

            localStorage.setItem(
                "firebase_user",
                JSON.stringify({{
                    uid: redirectResult.user.uid,
                    email: redirectResult.user.email,
                    name: redirectResult.user.displayName,
                    id_token: token
                }})
            );

            window.parent.location.reload();
        }}


        document.body.innerHTML = `
        <div style="
            max-width:430px;
            margin:40px auto;
            padding:30px;
            text-align:center;
            background:#1A0033;
            border:1px solid #5A189A;
            border-radius:14px;
            color:white;
        ">
            <h2>FraudShield AI</h2>

            <p>
            Sign in securely with your Google account.
            </p>

            <button id="login"
            style="
            width:100%;
            padding:13px;
            background:#7B2CBF;
            color:white;
            border:none;
            border-radius:8px;
            font-size:16px;
            ">
            Continue with Google
            </button>

            <p id="status"></p>
        </div>
        `;


        document
        .getElementById("login")
        .onclick = async () => {{

            const status =
            document.getElementById("status");

            status.innerHTML =
            "Signing in...";


            try {{

                const result =
                await signInWithRedirect(
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
        height=400,
    )


    user = st.session_state.get(
        "firebase_user"
    )

    return user