import streamlit as st
import requests
import json
import os
import logging

logger = logging.getLogger("fraudshield.chatbot")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")

ALLOWED_KEYWORDS = [
    "fraud", "transaction", "risk", "alert", "model", "prediction", "detect", 
    "suspicious", "anomaly", "investigation", "report", "dataset", "threshold", 
    "accuracy", "precision", "recall", "f1", "auc", "payment", "merchant", 
    "genuine", "training", "feature", "leakage", "fraudshield", "security", 
    "cyber", "money laundering", "aml", "financial crime", "audit", "compliance",
    "score", "classify", "bank", "credit", "debit", "upi", "phishing", "scam"
]

SYSTEM_PROMPT = (
    "You are the FraudShield AI Assistant, specialized exclusively in fraud detection, "
    "transaction analysis, risk scoring, alerts, model performance, reports, and dataset validation. "
    "You are part of the FraudShield AI platform. Only answer questions related to these domains. "
    "If asked about unrelated topics, politely decline."
)

LOCAL_FALLBACK = {
    "fraud": "Fraud detection identifies suspicious transactions using patterns like unusual amounts, new devices, or atypical locations. Our XGBoost model analyzes 25 features to flag potential fraud.",
    "risk": "Risk scores range from 0-100. Low (<30), Medium (30-60), High (60-85), Critical (>85). High and Critical transactions are flagged for investigation.",
    "model": "FraudShield uses XGBoost and RandomForest classifiers trained with SMOTE for class balancing. The best model is auto-selected based on F1-score.",
    "transaction": "Each transaction is analyzed across 25 features including amount, device, location, payment method, and behavioral patterns like time-of-day and recent activity.",
    "report": "Reports are available in the Reports tab. You can view fraud detection reports, investigation status, training metrics, and export data as CSV or JSON.",
    "prediction": "Predictions are made through the Predict page. Submit transaction details and get a real-time fraud probability, risk level, and recommendation from the trained model.",
    "default": "I can help with fraud detection, risk scoring, model performance, transaction analysis, and investigation workflows. What would you like to know?"
}

def check_relevance(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in ALLOWED_KEYWORDS)

def get_local_response(prompt):
    prompt_lower = prompt.lower()
    for key, response in LOCAL_FALLBACK.items():
        if key in prompt_lower:
            return response
    return LOCAL_FALLBACK["default"]

def call_openrouter(messages):
    """Call OpenRouter API. Returns (success, response_text, error_detail)."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://fraudshield-ai.local",
        "X-Title": "FraudShield AI"
    }
    
    # Filter to only user/assistant messages for the API, prepend system
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        if m["role"] in ("user", "assistant"):
            api_messages.append({"role": m["role"], "content": m["content"]})
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": api_messages,
        "max_tokens":500,
        "temperature":0.3
    }
    
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if res.status_code == 200:
            res_json = res.json()
            choices = res_json.get("choices", [])
            if choices and choices[0].get("message", {}).get("content"):
                return True, choices[0]["message"]["content"], None
            else:
                return False, None, f"Unexpected response format: {json.dumps(res_json)[:200]}"
        else:
            error_body = res.text[:300]
            logger.error(f"OpenRouter API error: HTTP {res.status_code} - {error_body}")
            return False, None, f"HTTP {res.status_code}: {error_body}"
            
    except requests.exceptions.Timeout:
        return False, None, "Request timed out after 30 seconds"
    except requests.exceptions.ConnectionError:
        return False, None, "Could not connect to OpenRouter API"
    except Exception as e:
        logger.error(f"OpenRouter exception: {type(e).__name__}: {e}")
        return False, None, f"{type(e).__name__}: {e}"

def render_chatbot():
    st.markdown(
        """
        <div class="chatbot-header">
            <h1>💬 FraudShield AI Assistant</h1>
            <p>Ask about fraud detection, transactions, risk scoring, alerts, and model performance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # API status
    if OPENROUTER_API_KEY:
        st.markdown(
            f"""
            <div class="chatbot-status online">
                🟢 AI Assistant Online
                <span>Model: {OPENROUTER_MODEL}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="chatbot-status fallback">
                🟡 Local Knowledge Mode
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        if not st.session_state.messages:
            st.markdown(
                """
                <div class="chatbot-welcome">
                    <h3>How can I help?</h3>
                    <p>
                        Ask questions about suspicious transactions, fraud patterns,
                        risk levels, model metrics, investigations, or reports.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
                
    if prompt := st.chat_input("Ask about fraud detection, models, or transactions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            # Topic filter
            if not check_relevance(prompt):
                response = "I can only assist with FraudShield AI, fraud detection, transactions, alerts, models, and reports. Please ask a fraud-related question."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                return
                
            # No API key → local fallback
            if not OPENROUTER_API_KEY:
                response = get_local_response(prompt)
                st.info("ℹ️ Local fallback mode (no API key configured)")
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                return
                
            # Call OpenRouter
            with st.spinner("Thinking..."):
                success, response, error_detail = call_openrouter(st.session_state.messages)
                
                if success:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    # Log real error, show friendly message, fall back to local
                    logger.error(f"OpenRouter failed: {error_detail}")
                    st.warning("⚠️ AI service unavailable. Using local knowledge base.")
                    local_response = get_local_response(prompt)
                    st.markdown(local_response)
                    st.session_state.messages.append({"role": "assistant", "content": local_response})
                    with st.expander("Debug Info (for developers)"):
                        st.code(error_detail)

if __name__ == "__main__":
    render_chatbot()
