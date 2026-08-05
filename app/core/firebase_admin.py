import os

import firebase_admin
from firebase_admin import credentials


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

SERVICE_ACCOUNT_PATH = os.path.join(
    PROJECT_ROOT,
    "firebase_service_account.json",
)


def initialize_firebase_admin():
    try:
        return firebase_admin.get_app()
    except ValueError:
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            raise FileNotFoundError(
                f"Firebase service account file not found: "
                f"{SERVICE_ACCOUNT_PATH}"
            )

        credential = credentials.Certificate(
            SERVICE_ACCOUNT_PATH
        )

        return firebase_admin.initialize_app(
            credential
        )


firebase_app = initialize_firebase_admin()