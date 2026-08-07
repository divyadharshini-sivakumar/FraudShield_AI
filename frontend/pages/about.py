import streamlit as st


def render_about():
    st.title("🛡️ FraudShield AI")

    st.markdown(
        """
        FraudShield AI is an intelligent fraud detection platform designed to
        analyze financial transactions, identify suspicious activity, and
        support fraud monitoring through machine learning and analytics.
        """
    )

    st.markdown("### ✨ Features")

    st.markdown(
        """
        **📊 Dashboard**  
        Provides an overview of transaction activity, fraud counts, genuine
        transactions, trends, merchant analysis, and fraud-related visualizations.

        **🔍 Prediction**  
        Allows users to enter transaction details and predict whether a transaction
        is likely to be fraudulent or legitimate.

        **📑 Reports**  
        Displays stored fraud detection results and useful information for
        reviewing previous predictions and transaction activity.

        **🤖 Chatbot**  
        Provides AI-assisted responses related to fraud detection, transaction
        analysis, and the FraudShield AI application.

        **⚙️ Train Model**  
        Allows users to upload their own CSV dataset, train fraud detection models,
        compare performance metrics, and identify the best-performing model.
        """
    )

    st.markdown("### 🧭 How to Use FraudShield AI")

    st.markdown(
        """
        **Step 1 — Dashboard**  
        Open the Dashboard to review transaction statistics and fraud analytics.

        **Step 2 — Prediction**  
        Enter transaction details in the Prediction page and click **Detect Fraud**.

        **Step 3 — Reports**  
        Open Reports to review previously recorded fraud detection information.

        **Step 4 — Chatbot**  
        Use the Chatbot to ask questions about fraud detection or transaction risk.

        **Step 5 — Train Model**  
        Upload a compatible CSV dataset and train a new fraud detection model.
        """
    )