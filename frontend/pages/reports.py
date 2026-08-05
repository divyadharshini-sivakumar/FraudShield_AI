import streamlit as st
import requests
import os
import json
import pandas as pd
import plotly.express as px

FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://127.0.0.1:8000")

def render_reports():
    st.title("📊 Reports & Analytics")
    
    try:
        health = requests.get(f"{FASTAPI_BASE_URL}/api/health", timeout=3)
        if health.status_code != 200:
            st.error("Backend not healthy.")
            return
    except Exception:
        st.error(f"Connection error: FastAPI backend is unreachable at {FASTAPI_BASE_URL}. Please start the backend.")
        return
        
    tab1, tab2, tab3, tab4 = st.tabs(["Fraud Detection Reports", "Investigation Reports", "Training Reports", "Exports"])
    
    with tab1:
        st.header("Fraud Detection Reports")
        try:
            res = requests.get(f"{FASTAPI_BASE_URL}/api/detections", timeout=10)
            if res.status_code == 200:
                data = res.json()
                if not data:
                    st.info("No detection records found. Run predictions from the Prediction page to generate records.")
                else:
                    df = pd.DataFrame(data)
                    
                    # --- Filters ---
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        risk_opts = [
                            "All",
                            "Low",
                            "Medium",
                            "High",
                            "Critical",
                        ]

                        risk_filter = st.selectbox(
                            "Risk Level",
                            options=risk_opts,
                            index=0,
                        )
                    with col2:
                        status_opts = [
                            "All",
                            "Pending",
                            "Under Review",
                            "Confirmed Fraud",
                            "False Positive",
                        ]

                        status_filter = st.selectbox(
                            "Investigation Status",
                            options=status_opts,
                            index=0,
                        )
                    with col3:
                        pred_opts = [
                            "All",
                            "Fraud",
                            "Legitimate",
                        ]

                        pred_filter = st.selectbox(
                            "Prediction",
                            options=pred_opts,
                            index=0,
                        )
                        
                    filtered_df = df.copy()
                    if risk_filter != "All":
                        filtered_df = filtered_df[
                            filtered_df["risk_level"] == risk_filter
                        ]

                    if status_filter != "All":
                        filtered_df = filtered_df[
                            filtered_df["investigation_status"] == status_filter
                        ]

                    if pred_filter != "All":
                        filtered_df = filtered_df[
                            filtered_df["fraud_prediction"] == pred_filter
                        ]
                    
                    # --- KPI Cards ---
                    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
                    total = len(filtered_df)
                    fraud_count = len(filtered_df[filtered_df["fraud_prediction"] == "Fraud"]) if "fraud_prediction" in filtered_df.columns else 0
                    high_risk = len(filtered_df[filtered_df["risk_level"].isin(["High", "Critical"])]) if "risk_level" in filtered_df.columns else 0
                    fraud_rate = (fraud_count / total * 100) if total > 0 else 0
                    avg_prob = filtered_df["fraud_probability"].mean() if "fraud_probability" in filtered_df.columns and total > 0 else 0
                    unresolved = len(filtered_df[filtered_df["investigation_status"] == "Pending"]) if "investigation_status" in filtered_df.columns else 0

                    kpi1.metric("📊 Total Detections", total)
                    kpi2.metric("🚨 Fraud Alerts", fraud_count)
                    kpi3.metric("⚠ High Risk", high_risk)
                    kpi4.metric("🎯 Fraud Rate", f"{fraud_rate:.1f}%")
                    kpi5.metric("🎯 Avg Fraud Probability", f"{avg_prob:.3f}")
                    kpi6.metric("📝 Pending Review", unresolved)
                    
                    st.markdown("---")
                    
                    # --- Charts ---
                    if not filtered_df.empty:
                        chart1, chart2 = st.columns(2)
                        
                        with chart1:
                            if "prediction_timestamp" in filtered_df.columns:
                                temp = filtered_df.copy()
                                temp["date"] = pd.to_datetime(temp["prediction_timestamp"]).dt.date
                                timeline = temp.groupby(["date", "fraud_prediction"]).size().reset_index(name="count")
                                fig = px.line(timeline, x="date", y="count", color="fraud_prediction",
                                              title="Detections Over Time",
                                              color_discrete_map={"Fraud": "#ff4b4b", "Legitimate": "#00cc96"})
                                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                                  font_color="#E0AAFF", legend_title_text="Prediction")
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with chart2:
                            if "risk_level" in filtered_df.columns:
                                risk_counts = filtered_df["risk_level"].value_counts().reset_index()
                                risk_counts.columns = ["risk_level", "count"]
                                fig2 = px.bar(risk_counts, x="risk_level", y="count", title="By Risk Level",
                                              color="risk_level",
                                              color_discrete_map={"Low": "#00cc96", "Medium": "#ffa15a", "High": "#ff4b4b", "Critical": "#d62728"})
                                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                                   font_color="#E0AAFF", showlegend=False)
                                st.plotly_chart(fig2, use_container_width=True)
                        
                        chart3, chart4 = st.columns(2)
                        with chart3:
                            if "merchant_category" in filtered_df.columns:
                                fig3 = px.bar(filtered_df, x="merchant_category", color="fraud_prediction",
                                              title="By Merchant Category",
                                              color_discrete_map={"Fraud": "#ff4b4b", "Legitimate": "#00cc96"})
                                fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                                   font_color="#E0AAFF")
                                st.plotly_chart(fig3, use_container_width=True)
                        with chart4:
                            if "payment_method" in filtered_df.columns:
                                fig4 = px.pie(filtered_df, names="payment_method", title="By Payment Method")
                                fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#E0AAFF")
                                st.plotly_chart(fig4, use_container_width=True)
                    
                    # --- Detections Table ---
                    st.subheader("Detection Records")
                    cols_to_show = ["id", "prediction_timestamp", "amount", "merchant", "fraud_prediction",
                                    "fraud_probability", "risk_level", "risk_score", "investigation_status", "model_name"]
                    available_cols = [c for c in cols_to_show if c in filtered_df.columns]
                    display_df = filtered_df[available_cols].copy()
                    if "fraud_probability" in display_df.columns:
                        display_df["fraud_probability"] = display_df["fraud_probability"].round(4)
                    if "risk_score" in display_df.columns:
                        display_df["risk_score"] = display_df["risk_score"].round(2)
                    st.dataframe(display_df.head(100), use_container_width=True)
            else:
                st.error(f"Failed to load detections (HTTP {res.status_code}).")
        except Exception as e:
            st.error(f"Error loading detections: {type(e).__name__}: {e}")
            
    with tab2:
        st.header("Investigation Reports")
        det_id = st.text_input("Enter Detection ID to Investigate")
        if det_id:
            try:
                res = requests.get(f"{FASTAPI_BASE_URL}/api/detections/{det_id}", timeout=10)
                if res.status_code == 200:
                    record = res.json()
                    
                    # Display as structured card
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Transaction ID:** {record.get('transaction_id', 'N/A')}")
                        st.markdown(f"**Amount:** ₹{record.get('amount', 0):,.2f}")
                        st.markdown(f"**Merchant:** {record.get('merchant', 'N/A')}")
                        st.markdown(f"**Category:** {record.get('merchant_category', 'N/A')}")
                        st.markdown(f"**Payment:** {record.get('payment_method', 'N/A')} / {record.get('payment_channel', 'N/A')}")
                        st.markdown(f"**Location:** {record.get('city', 'N/A')}, {record.get('state', 'N/A')}, {record.get('country', 'N/A')}")
                        st.markdown(f"**Device:** {record.get('device_type', 'N/A')}")
                    with col2:
                        pred = record.get('fraud_prediction', 'Unknown')
                        if pred == "Fraud":
                            st.error(f"🚨 Prediction: {pred}")
                        else:
                            st.success(f"✅ Prediction: {pred}")
                        st.markdown(f"**Fraud Probability:** {record.get('fraud_probability', 0):.4f}")
                        st.markdown(f"**Risk Score:** {record.get('risk_score', 0):.2f}")
                        st.markdown(f"**Risk Level:** {record.get('risk_level', 'N/A')}")
                        st.markdown(f"**Model:** {record.get('model_name', 'N/A')} v{record.get('model_version', 'N/A')}")
                        st.markdown(f"**Timestamp:** {record.get('prediction_timestamp', 'N/A')}")
                        st.markdown(f"**Latency:** {record.get('prediction_latency_ms', 0):.1f} ms")
                    
                    if record.get("anomaly_factors"):
                        st.subheader("Anomaly Factors")
                        for f in record["anomaly_factors"]:
                            st.markdown(f"- ⚠️ {f}")
                    
                    if record.get("recommendation"):
                        st.info(f"**Recommendation:** {record['recommendation']}")
                    
                    st.markdown("---")
                    st.subheader("Update Investigation")
                    current_status = record.get("investigation_status", "Pending")
                    status_options = ["Pending", "Under Review", "Confirmed Fraud", "False Positive", "Resolved"]
                    current_idx = status_options.index(current_status) if current_status in status_options else 0
                    status = st.selectbox("Investigation Status", status_options, index=current_idx)
                    notes = st.text_area("Analyst Notes", value=record.get("analyst_notes", "") or "")
                    if st.button("Save Investigation"):
                        update_res = requests.put(
                            f"{FASTAPI_BASE_URL}/api/detections/{det_id}/investigate", 
                            json={"investigation_status": status, "analyst_notes": notes},
                            timeout=10
                        )
                        if update_res.status_code == 200:
                            st.success("✅ Investigation updated successfully.")
                            st.rerun()
                        else:
                            st.error(f"Failed to update investigation (HTTP {update_res.status_code}).")
                    
                    with st.expander("View Raw Record"):
                        st.json(record)
                elif res.status_code == 404:
                    st.warning(f"Detection ID {det_id} not found.")
                else:
                    st.error(f"Error fetching detection (HTTP {res.status_code}).")
            except Exception as e:
                st.error(f"Error: {type(e).__name__}: {e}")
                
    with tab3:
        st.header("Training Reports")
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        if os.path.exists(reports_dir):
            reports = sorted([f for f in os.listdir(reports_dir) if f.endswith(".json")], reverse=True)
            if reports:
                selected_report = st.selectbox("Select Report", reports)
                if selected_report:
                    with open(os.path.join(reports_dir, selected_report), "r") as f:
                        report_data = json.load(f)
                    
                    col1, col2 = st.columns(2)

                    # Read whichever keys exist in the report
                    model = report_data.get("model_name") or report_data.get("best_model")
                    trained = report_data.get("training_timestamp") or report_data.get("timestamp")
                    dataset = report_data.get("dataset_path")
                    target = report_data.get("target")

                    feature_count = None
                    if "feature_count" in report_data:
                        feature_count = report_data["feature_count"]
                    elif "features" in report_data:
                        cats = report_data["features"].get("categorical", [])
                        nums = report_data["features"].get("numeric", [])
                        feature_count = len(cats) + len(nums)

                    with col1:
                        if model:
                            st.markdown(f"**Model:** {model}")

                        if trained:
                            st.markdown(f"**Trained at:** {trained}")

                        if feature_count is not None:
                            st.markdown(f"**Feature Count:** {feature_count}")

                    with col2:
                        if dataset:
                            st.markdown(f"**Dataset:** {dataset}")

                        if target:
                            st.markdown(f"**Target:** {target}")
                    
                    st.subheader("Metrics")
                    metrics = report_data.get("metrics", {})
                    if metrics:
                        mcols = st.columns(len(metrics))
                        for i, (k, v) in enumerate(metrics.items()):
                            mcols[i % len(mcols)].metric(k.replace("_", " ").title(), f"{v:.4f}" if isinstance(v, float) else str(v))
                    
                    if "leakage_audit" in report_data:
                        audit = report_data["leakage_audit"]
                        if audit.get("leakage_detected"):
                            st.warning("⚠️ Data Leakage Detected During Training")
                            st.write("Excluded Columns:", audit.get("excluded_columns", []))
                        else:
                            st.success("✅ No leakage detected.")
                            
                    with st.expander("View Raw JSON"):
                        st.text_area(
                            label="",
                            value=json.dumps(report_data, indent=4),
                            height=500,
                            disabled=False,
                            key=f"raw_report_{selected_report}",
                        )
            else:
                st.info("No training reports found.")
        else:
            st.info("Reports directory does not exist yet. Train a model to generate reports.")
            
    with tab4:
        st.header("Export Detection Records")
        st.markdown("Download all detection records in your preferred format:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"📄 [Download as CSV]({FASTAPI_BASE_URL}/api/detections/export/csv)")
        with col2:
            st.markdown(f"📋 [Download as JSON]({FASTAPI_BASE_URL}/api/detections/export/json)")

if __name__ == "__main__":
    render_reports()
