import os
import random

import plotly.graph_objects as go
import requests
import streamlit as st


FASTAPI_BASE_URL = os.environ.get(
    "FASTAPI_BASE_URL",
    "http://127.0.0.1:8000",
)


def check_backend():
    """Check whether the FastAPI backend is available."""
    try:
        response = requests.get(
            f"{FASTAPI_BASE_URL}/api/health",
            timeout=3,
        )

        if response.status_code == 200:
            return True, response.json()

    except requests.exceptions.RequestException:
        pass

    return False, None


def render_predict():
    st.title("🛡️ Fraud Prediction")
    st.caption(
        "Enter transaction details to calculate fraud probability and risk level."
    )

    is_up, health_data = check_backend()

    if is_up:
        st.success("🟢 Prediction system is online")
    else:
        st.error(
            "🔴 Prediction system is offline. Start the FastAPI backend "
            "before using real-model prediction."
        )

    st.markdown(
        """
        <style>
        .metric-card {
            background-color: rgba(60, 9, 108, 0.30);
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 10px;
            border: 1px solid #5A189A;
        }

        .fraud-label {
            color: #FF4B4B !important;
            font-weight: 700;
            font-size: 25px;
            margin-bottom: 10px;
        }

        .genuine-label {
            color: #00CC96 !important;
            font-weight: 700;
            font-size: 25px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    demo_mode = st.checkbox(
        "Enable Demo Mode",
        help="Demo mode uses simulated results instead of the trained model.",
    )

    with st.form("prediction_form"):
        # ======================================================
        # PERSONAL DETAILS
        # ======================================================
        st.subheader("Personal Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                value=None,
                placeholder="Enter customer age",
            )

        with col2:
            gender = st.selectbox(
                "Gender",
                options=["Male", "Female", "Other"],
                index=None,
                placeholder="Select gender",
            )

        with col3:
            occupation = st.selectbox(
                "Occupation",
                options=[
                    "Salaried",
                    "Business",
                    "Student",
                    "Self Employed",
                    "Retired",
                    "Other",
                ],
                index=None,
                placeholder="Select occupation",
            )

        # ======================================================
        # ACCOUNT DETAILS
        # ======================================================
        st.subheader("Account Details")

        account_age = st.number_input(
            "Account Age (Months)",
            min_value=0,
            max_value=600,
            value=None,
            placeholder="Enter account age in months",
        )

        # ======================================================
        # TRANSACTION DETAILS
        # ======================================================
        st.subheader("Transaction Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=None,
                placeholder="Enter transaction amount",
            )

        with col2:
            transaction_type = st.selectbox(
                "Transaction Type",
                options=[
                    "Purchase",
                    "Transfer",
                    "Bill Payment",
                    "Subscription",
                ],
                index=None,
                placeholder="Select transaction type",
            )

        with col3:
            currency = st.selectbox(
                "Currency",
                options=["INR"],
                index=None,
                placeholder="Select currency",
            )

        # ======================================================
        # PAYMENT DETAILS
        # ======================================================
        st.subheader("Payment Details")

        col1, col2 = st.columns(2)

        with col1:
            payment_method = st.selectbox(
                "Payment Method",
                options=[
                    "Credit Card",
                    "Debit Card",
                    "UPI",
                    "Net Banking",
                ],
                index=None,
                placeholder="Select payment method",
            )

        with col2:
            payment_channel = st.selectbox(
                "Payment Channel",
                options=[
                    "Mobile App",
                    "Web",
                    "POS",
                    "ATM",
                ],
                index=None,
                placeholder="Select payment channel",
            )

        # ======================================================
        # MERCHANT DETAILS
        # ======================================================
        st.subheader("Merchant Details")

        col1, col2 = st.columns(2)

        with col1:
            merchant_name = st.text_input(
                "Merchant Name",
                value="",
                placeholder="Enter merchant name",
            )

        with col2:
            merchant_category = st.selectbox(
                "Merchant Category",
                options=[
                    "Shopping",
                    "Electronics",
                    "Food",
                    "Groceries",
                    "Travel",
                    "Entertainment",
                    "Utilities",
                    "Banking",
                    "Other",
                ],
                index=None,
                placeholder="Select merchant category",
            )

        # ======================================================
        # LOCATION
        # ======================================================
        st.subheader("Location")

        col1, col2, col3 = st.columns(3)

        with col1:
            city = st.text_input(
                "City",
                value="",
                placeholder="Enter city",
            )

        with col2:
            state = st.text_input(
                "State",
                value="",
                placeholder="Enter state",
            )

        with col3:
            country = st.selectbox(
                "Country",
                options=["India"],
                index=0,
            )

        # ======================================================
        # DEVICE AND NETWORK
        # ======================================================
        st.subheader("Device & Network")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            device_type = st.selectbox(
                "Device Type",
                options=[
                    "Mobile",
                    "Laptop",
                    "Tablet",
                    "Desktop",
                ],
                index=None,
                placeholder="Select device",
            )

        with col2:
            operating_system = st.selectbox(
                "Operating System",
                options=[
                    "Android",
                    "iOS",
                    "Windows",
                    "macOS",
                    "Linux",
                ],
                index=None,
                placeholder="Select OS",
            )

        with col3:
            browser = st.selectbox(
                "Browser",
                options=[
                    "Chrome",
                    "Safari",
                    "Firefox",
                    "Edge",
                ],
                index=None,
                placeholder="Select browser",
            )

        with col4:
            network_type = st.selectbox(
                "Network Type",
                options=[
                    "WiFi",
                    "4G",
                    "5G",
                    "Public WiFi",
                ],
                index=None,
                placeholder="Select network",
            )

        # ======================================================
        # RISK FLAGS
        # ======================================================
        st.subheader("Risk Flags")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            is_new_device = st.checkbox("Is New Device")

        with col2:
            is_new_location = st.checkbox("Is New Location")

        with col3:
            outside_normal_hours = st.checkbox(
                "Outside Normal Hours"
            )

        with col4:
            merchant_previously_used = st.checkbox(
                "Merchant Previously Used"
            )

        # ======================================================
        # NUMERIC BEHAVIOURAL FEATURES
        # ======================================================
        st.subheader("Behavioural Features")

        col1, col2, col3 = st.columns(3)

        with col1:
            amount_deviation = st.number_input(
                "Amount Deviation",
                min_value=0.0,
                value=None,
                placeholder="Enter deviation value",
                help=(
                    "How different this amount is from the customer's "
                    "normal spending pattern."
                ),
            )

        with col2:
            previous_transactions_24h = st.number_input(
                "Previous Transactions (24H)",
                min_value=0,
                value=None,
                placeholder="Enter transaction count",
            )

        with col3:
            transactions_last_10_min = st.number_input(
                "Transactions in Last 10 Minutes",
                min_value=0,
                value=None,
                placeholder="Enter transaction count",
            )

        submitted = st.form_submit_button(
            "Detect Fraud",
            use_container_width=True,
        )

    # ==========================================================
    # VALIDATION
    # ==========================================================
    if submitted:
        required_fields = {
            "Age": age,
            "Gender": gender,
            "Occupation": occupation,
            "Account Age": account_age,
            "Amount": amount,
            "Transaction Type": transaction_type,
            "Currency": currency,
            "Payment Method": payment_method,
            "Payment Channel": payment_channel,
            "Merchant Name": merchant_name.strip(),
            "Merchant Category": merchant_category,
            "City": city.strip(),
            "State": state.strip(),
            "Device Type": device_type,
            "Operating System": operating_system,
            "Browser": browser,
            "Network Type": network_type,
            "Amount Deviation": amount_deviation,
            "Previous Transactions 24H": previous_transactions_24h,
            "Transactions Last 10 Minutes": transactions_last_10_min,
        }

        missing_fields = [
            field_name
            for field_name, field_value in required_fields.items()
            if field_value is None or field_value == ""
        ]

        if missing_fields:
            st.warning(
                "Please complete the following fields: "
                + ", ".join(missing_fields)
            )
            return

        if not is_up and not demo_mode:
            st.error(
                "Cannot run prediction because the backend is offline. "
                "Start FastAPI or enable Demo Mode."
            )
            return

        payload = {
            "Age": age,
            "Gender": gender,
            "Occupation": occupation,
            "Account_Age_Months": account_age,
            "Amount": amount,
            "Transaction_Type": transaction_type,
            "Currency": currency,
            "Payment_Method": payment_method,
            "Payment_Channel": payment_channel,
            "Merchant_Name": merchant_name.strip(),
            "Merchant_Category": merchant_category,
            "City": city.strip(),
            "State": state.strip(),
            "Country": country,
            "Device_Type": device_type,
            "Operating_System": operating_system,
            "Browser": browser,
            "Network_Type": network_type,
            "Is_New_Device": "Yes" if is_new_device else "No",
            "Is_New_Location": "Yes" if is_new_location else "No",
            "Outside_Normal_Hours": (
                "Yes" if outside_normal_hours else "No"
            ),
            "Merchant_Previously_Used": (
                "Yes" if merchant_previously_used else "No"
            ),
            "Amount_Deviation": amount_deviation,
            "Previous_Transactions_24H": previous_transactions_24h,
            "Transactions_Last_10_Min": transactions_last_10_min,
        }

        # ======================================================
        # PREDICTION
        # ======================================================
        with st.spinner("Analyzing transaction..."):
            if demo_mode:
                probability = random.uniform(0, 1)
                is_fraud = probability >= 0.5

                result = {
                    "Prediction": (
                        "Fraud" if is_fraud else "Legitimate"
                    ),
                    "Probability": probability,
                    "Risk_Level": (
                        "Critical"
                        if probability >= 0.85
                        else "High"
                        if probability >= 0.60
                        else "Medium"
                        if probability >= 0.30
                        else "Low"
                    ),
                    "Model_Info": "Demo Simulated Model",
                    "Model_Version": "Demo",
                    "Threshold": 0.5,
                    "Contributing_Factors": {
                        "Amount": amount,
                        "Outside Normal Hours": outside_normal_hours,
                    },
                    "Recommendation": (
                        "Investigate"
                        if is_fraud
                        else "Approve"
                    ),
                }

                st.warning(
                    "Demo Mode is enabled. This is not trained-model output."
                )

            else:
                try:
                    api_payload = {
                        "transaction_data": payload
                    }

                    response = requests.post(
                        f"{FASTAPI_BASE_URL}/api/predict",
                        json=api_payload,
                        timeout=30,
                    )

                    if response.status_code != 200:
                        st.error(
                            f"Prediction API error "
                            f"(HTTP {response.status_code}): "
                            f"{response.text}"
                        )
                        return

                    api_result = response.json()

                    result = {
                        "Prediction": api_result.get(
                            "prediction",
                            "Unknown",
                        ),
                        "Probability": api_result.get(
                            "fraud_probability",
                            0.0,
                        ),
                        "Risk_Level": api_result.get(
                            "risk_level",
                            "Unknown",
                        ),
                        "Model_Info": api_result.get(
                            "model_name",
                            "N/A",
                        ),
                        "Model_Version": api_result.get(
                            "model_version",
                            "N/A",
                        ),
                        "Threshold": api_result.get(
                            "applied_threshold",
                            0.5,
                        ),
                        "Dataset_Source": api_result.get(
                            "dataset_source",
                            "N/A",
                        ),
                        "Detection_ID": api_result.get(
                            "detection_id",
                        ),
                        "Timestamp": api_result.get(
                            "prediction_timestamp",
                            "N/A",
                        ),
                        "Recommendation": api_result.get(
                            "recommendation",
                            "N/A",
                        ),
                        "Contributing_Factors": {
                            factor: "Detected"
                            for factor in api_result.get(
                                "contributing_factors",
                                [],
                            )
                        },
                    }

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Cannot connect to the prediction backend."
                    )
                    return

                except requests.exceptions.Timeout:
                    st.error(
                        "Prediction request timed out. Please try again."
                    )
                    return

                except Exception as exc:
                    st.error(f"Prediction failed: {exc}")
                    return

        # ======================================================
        # DISPLAY RESULTS
        # ======================================================
        st.markdown("---")
        st.subheader("Prediction Results")

        prediction_class = result.get(
            "Prediction",
            "Unknown",
        )
        probability = float(
            result.get("Probability", 0.0)
        )
        risk_level = result.get(
            "Risk_Level",
            "Unknown",
        )

        result_col, gauge_col = st.columns([1, 2])

        with result_col:
            st.markdown(
                '<div class="metric-card">',
                unsafe_allow_html=True,
            )

            if prediction_class == "Fraud":
                st.markdown(
                    '<div class="fraud-label">'
                    '🚨 FRAUD DETECTED'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="genuine-label">'
                    '✅ LEGITIMATE TRANSACTION'
                    '</div>',
                    unsafe_allow_html=True,
                )

            st.metric("Risk Level", risk_level)

            st.markdown(
                f"**Model:** {result.get('Model_Info', 'N/A')}"
            )
            st.markdown(
                f"**Version:** {result.get('Model_Version', 'N/A')}"
            )
            st.markdown(
                f"**Threshold:** {result.get('Threshold', 0.5)}"
            )
            st.markdown(
                f"**Recommendation:** "
                f"{result.get('Recommendation', 'N/A')}"
            )

            if result.get("Detection_ID") is not None:
                st.markdown(
                    f"**Detection ID:** "
                    f"{result['Detection_ID']}"
                )
                st.markdown(
                    f"**Timestamp:** "
                    f"{result.get('Timestamp', 'N/A')}"
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        with gauge_col:
            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=probability * 100,
                    number={
                        "suffix": "%",
                        "font": {"color": "white"},
                    },
                    title={
                        "text": "Fraud Probability",
                        "font": {"color": "white"},
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100],
                            "tickcolor": "white",
                        },
                        "bar": {
                            "color": "#9D4EDD",
                        },
                        "steps": [
                            {
                                "range": [0, 30],
                                "color": "rgba(0,204,150,0.30)",
                            },
                            {
                                "range": [30, 60],
                                "color": "rgba(255,161,90,0.30)",
                            },
                            {
                                "range": [60, 85],
                                "color": "rgba(255,75,75,0.30)",
                            },
                            {
                                "range": [85, 100],
                                "color": "rgba(214,39,40,0.40)",
                            },
                        ],
                        "threshold": {
                            "line": {
                                "color": "#FF4B4B",
                                "width": 4,
                            },
                            "thickness": 0.75,
                            "value": (
                                float(
                                    result.get(
                                        "Threshold",
                                        0.5,
                                    )
                                )
                                * 100
                            ),
                        },
                    },
                )
            )

            gauge.update_layout(
                height=280,
                margin=dict(
                    l=20,
                    r=20,
                    t=50,
                    b=20,
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font={
                    "color": "white",
                },
            )

            st.plotly_chart(
                gauge,
                use_container_width=True,
            )

        st.subheader("Contributing Factors")

        factors = result.get(
            "Contributing_Factors",
            {},
        )

        if factors:
            for factor_name, factor_value in factors.items():
                st.markdown(
                    f"- **{factor_name}:** {factor_value}"
                )
        else:
            st.info(
                "No specific contributing factors were returned."
            )


if __name__ == "__main__":
    render_predict()