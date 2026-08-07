import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json


# =========================
# Load Dataset
# =========================
def get_active_dataset_path():
    if "active_dataset_path" in st.session_state:
        return st.session_state["active_dataset_path"]

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )

    settings_file = os.path.join(
        project_root,
        "active_dataset.json"
    )

    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            path = data.get("active_dataset_path")

            if path:
                st.session_state["active_dataset_path"] = path
                return path
        except Exception:
            pass

    return os.path.join(
        project_root,
        "historical_transactions.csv"
    )


def load_data():
    csv_path = get_active_dataset_path()

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)

            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(
                    df["Timestamp"],
                    errors="coerce"
                )

            return df

        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            return None

    
    return None
# =========================
# Dashboard
# =========================
def render_dashboard():

    st.title("🛡 Fraud Analytics Dashboard")
    st.caption(
        "Real-time monitoring and intelligent analysis of financial transactions."
    )
    settings_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "active_dataset.json"
    )

    dataset_name = "No dataset selected"

    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)

            dataset_path = settings.get("active_dataset_path", "")

            if dataset_path:
                dataset_name = os.path.basename(dataset_path)

        except Exception:
            pass

    

    df = load_data()

    if df is None:
        st.info(
            """
            📊 **Dashboard ready**

            No historical dataset is loaded yet.

            Go to **Train Model**, upload a CSV file, and start training.
            The dashboard will display analytics after a dataset is available.
            """
        )
        return

    # =========================
    # KPI SECTION
    # =========================

    total_transactions = len(df)

    fraud_count = (
        int(df["Fraud_Label"].sum())
        if "Fraud_Label" in df.columns
        else 0
    )

    genuine_count = total_transactions - fraud_count

    fraud_rate = (
        (fraud_count / total_transactions) * 100
        if total_transactions > 0
        else 0
    )

    average_amount = (
        df["Amount"].mean()
        if "Amount" in df.columns
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📊 Transactions",
        f"{total_transactions:,}"
    )

    col2.metric(
        "🚨 Fraud",
        f"{fraud_count:,}"
    )

    col3.metric(
        "✅ Genuine",
        f"{genuine_count:,}"
    )

    col4.metric(
        "💰 Avg Amount",
        f"₹ {average_amount:,.2f}"
    )

    st.write("")

    # =========================
    # FIRST ROW
    # =========================

    left, right = st.columns(2)

    # =========================
    # PIE CHART
    # =========================

    if "Fraud_Label" in df.columns:

        pie_df = (
            df["Fraud_Label"]
            .value_counts()
            .reset_index()
        )

        pie_df.columns = ["Status", "Count"]

        pie_df["Status"] = pie_df["Status"].replace(
            {
                0: "Genuine",
                1: "Fraud"
            }
        )

        fig_pie = px.pie(
            pie_df,
            names="Status",
            values="Count",
            hole=0.55,
            color="Status",
            title="Transaction Distribution",
            color_discrete_map={
                "Fraud": "#FF4B4B",
                "Genuine": "#6A5ACD"
            }
        )

        fig_pie.update_layout(

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(
                color="white",
                size=14
            ),

            title=dict(
                font=dict(
                    size=22,
                    color="white"
                ),
                x=0.02
            ),

            legend=dict(
                font=dict(
                    color="white",
                    size=13
                )
            ),

            margin=dict(
                l=20,
                r=20,
                t=70,
                b=20
            )
        )

        left.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    # =========================
    # MERCHANT CHART
    # =========================

    if (
        "Merchant_Category" in df.columns
        and
        "Fraud_Label" in df.columns
    ):

        merchant_df = (
            df[df["Fraud_Label"] == 1]
            .groupby("Merchant_Category")
            .size()
            .reset_index(name="Count")
            .sort_values(
                "Count",
                ascending=False
            )
            .head(10)
        )

        fig_bar = px.bar(
            merchant_df,
            x="Merchant_Category",
            y="Count",
            title="Top Fraud by Merchant",
            color_discrete_sequence=["#9D4EDD"]
        )

        fig_bar.update_layout(

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(
                color="white",
                size=14
            ),

            title=dict(
                font=dict(
                    color="white",
                    size=22
                ),
                x=0.02
            ),

            xaxis=dict(
                title="Merchant",
                title_font=dict(color="white"),
                tickfont=dict(color="white"),
                showgrid=False
            ),

            yaxis=dict(
                title="Fraud Count",
                title_font=dict(color="white"),
                tickfont=dict(color="white"),
                gridcolor="rgba(255,255,255,0.08)"
            ),

            margin=dict(
                l=20,
                r=20,
                t=70,
                b=20
            )
        )

        right.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    
    # ==========================================================
    # SECOND ROW
    # ==========================================================

    st.write("")

    left2, right2 = st.columns(2)

    # ---------------- Amount Distribution ----------------

    if "Amount" in df.columns:

        fig_hist = px.histogram(
            df,
            x="Amount",
            color="Fraud_Label" if "Fraud_Label" in df.columns else None,
            nbins=40,
            title="Transaction Amount Distribution",
            color_discrete_map={
                0: "#6A5ACD",
                1: "#FF4B4B"
            }
        )

        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(color="white", size=14),

            title=dict(
                font=dict(color="white", size=22),
                x=0.02
            ),

            xaxis=dict(
                title="Amount",
                title_font=dict(color="white"),
                tickfont=dict(color="white"),
                showgrid=False
            ),

            yaxis=dict(
                title="Transactions",
                title_font=dict(color="white"),
                tickfont=dict(color="white"),
                gridcolor="rgba(255,255,255,0.08)"
            )
        )

        left2.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    # ---------------- Fraud Trend ----------------

    if "Timestamp" in df.columns and "Fraud_Label" in df.columns:

        temp = df.copy()

        temp["Date"] = temp["Timestamp"].dt.date

        trend = (
            temp[temp["Fraud_Label"] == 1]
            .groupby("Date")
            .size()
            .reset_index(name="Fraud Count")
        )

        fig_line = px.line(
            trend,
            x="Date",
            y="Fraud Count",
            title="Fraud Trend Over Time"
        )

        fig_line.update_traces(
            line=dict(
                color="#FF4B4B",
                width=3
            )
        )

        fig_line.update_layout(

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(color="white", size=14),

            title=dict(
                font=dict(color="white", size=22),
                x=0.02
            ),

            xaxis=dict(
                title_font=dict(color="white"),
                tickfont=dict(color="white")
            ),

            yaxis=dict(
                title_font=dict(color="white"),
                tickfont=dict(color="white"),
                gridcolor="rgba(255,255,255,0.08)"
            )
        )

        right2.plotly_chart(
            fig_line,
            use_container_width=True
        )

    # ==========================================================
    # THIRD ROW
    # ==========================================================

    if (
        "Payment_Method" in df.columns
        and
        "Fraud_Label" in df.columns
    ):

        st.write("")

        left3, right3 = st.columns(2)

        payment = (
            df[df["Fraud_Label"] == 1]
            .groupby("Payment_Method")
            .size()
            .reset_index(name="Count")
        )

        fig_payment = px.bar(
            payment,
            x="Payment_Method",
            y="Count",
            title="Fraud by Payment Method",
            color_discrete_sequence=["#9D4EDD"]
        )

        fig_payment.update_layout(

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(color="white", size=14),

            title=dict(
                font=dict(color="white", size=22),
                x=0.02
            ),

            xaxis=dict(
                title_font=dict(color="white"),
                tickfont=dict(color="white")
            ),

            yaxis=dict(
                title_font=dict(color="white"),
                tickfont=dict(color="white"),
                gridcolor="rgba(255,255,255,0.08)"
            )
        )

        left3.plotly_chart(
            fig_payment,
            use_container_width=True
        )

        # ---------------- Risk Score ----------------

        if "Risk_Score" in df.columns:

            fig_risk = px.histogram(
                df,
                x="Risk_Score",
                color="Fraud_Label",
                nbins=25,
                title="Risk Score Distribution",
                color_discrete_map={
                    0: "#6A5ACD",
                    1: "#FF4B4B"
                }
            )

            fig_risk.update_layout(

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                font=dict(color="white", size=14),

                title=dict(
                    font=dict(color="white", size=22),
                    x=0.02
                ),

                xaxis=dict(
                    title_font=dict(color="white"),
                    tickfont=dict(color="white")
                ),

                yaxis=dict(
                    title_font=dict(color="white"),
                    tickfont=dict(color="white"),
                    gridcolor="rgba(255,255,255,0.08)"
                )
            )

            right3.plotly_chart(
                fig_risk,
                use_container_width=True
            )

   

    # ==========================================================
    # FRAUD TRANSACTION DETAILS
    # ==========================================================

    st.write("")
    st.markdown("---")
    st.subheader("🚨 Fraud Transaction Details")

    if "Fraud_Label" in df.columns:
        fraud_mask = (
            df["Fraud_Label"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["1", "fraud", "fraudulent", "yes", "true"])
        )

        fraud_transactions = df[fraud_mask].copy()

        if not fraud_transactions.empty:
            preferred_columns = [
                "Transaction_ID",
                "Timestamp",
                "Amount",
                "Merchant",
                "Merchant_Category",
                "Payment_Method",
                "Payment_Channel",
                "City",
                "State",
                "Country",
                "Device_Type",
                "Risk_Score",
                "Fraud_Label",
            ]

            available_columns = [
                column
                for column in preferred_columns
                if column in fraud_transactions.columns
            ]

            fraud_table = (
                fraud_transactions[available_columns]
                if available_columns
                else fraud_transactions
            )

            st.caption(
                f"Showing {len(fraud_transactions):,} fraudulent transactions "
                "from the current dataset."
            )

            st.dataframe(
                fraud_table,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.success(
                "✅ No fraudulent transactions found in the current dataset."
            )

    else:
        st.info(
            "Fraud transaction details are unavailable because "
            "the dataset does not contain a Fraud_Label column."
        )

    st.success("✔ Dashboard updated successfully.")