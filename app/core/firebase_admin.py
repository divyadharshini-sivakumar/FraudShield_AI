import json
import os

import firebase_admin
from firebase_admin import credentials


def initialize_firebase_admin():
    try:
        return firebase_admin.get_app()

    except ValueError:
        service_account_json = os.getenv(
            "FIREBASE_SERVICE_ACCOUNT_JSON",
            "",
        )

        if service_account_json:
            try:
                service_account_info = json.loads(
                    service_account_json
                )
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "FIREBASE_SERVICE_ACCOUNT_JSON is invalid."
                ) from exc

            credential = credentials.Certificate(
                service_account_info
            )

            return firebase_admin.initialize_app(
                credential
            )

        # Local development fallback
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )

        service_account_path = os.path.join(
            project_root,
            "firebase_service_account.json",
        )

        if not os.path.exists(service_account_path):
            raise FileNotFoundError(
                "Firebase credentials are not configured."
            )

        credential = credentials.Certificate(
            service_account_path
        )

        return firebase_admin.initialize_app(
            credential
        )


firebase_app = initialize_firebase_admin()