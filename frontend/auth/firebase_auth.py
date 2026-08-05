import os

import pyrebase
from dotenv import load_dotenv


load_dotenv()


firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": "",
}


def get_firebase_auth():
    required_values = {
        key: value
        for key, value in firebase_config.items()
        if key != "databaseURL"
    }

    missing = [
        key
        for key, value in required_values.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing Firebase configuration: "
            + ", ".join(missing)
        )

    firebase = pyrebase.initialize_app(firebase_config)
    return firebase.auth()