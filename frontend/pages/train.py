import json
import os
import time
from datetime import datetime

import streamlit as st

from app.models.trainer import ModelTrainer


def render_train():
    st.title("🧠 Train Model")
    st.caption("Train and review a fraud detection model using your selected dataset.")

    data_path = st.text_input(
        "Dataset Path (CSV)",
        value="",
        placeholder="Browse or paste the full path to your dataset...",
        help="Enter the path to the CSV file used for training.",
    )

    if st.button("Start Training", use_container_width=True):
        active_dataset_path = data_path.strip().strip('"')
        

        if not active_dataset_path:
            st.error("Please enter a dataset path.")
            return

        if not os.path.exists(active_dataset_path):
            st.error(f"Dataset not found: {active_dataset_path}")
            return

        st.session_state["active_dataset_path"] = active_dataset_path

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )

        settings_path = os.path.join(
            project_root,
            "active_dataset.json",
        )

        with open(settings_path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "active_dataset_path": active_dataset_path
                },
                file,
                indent=4,
            )

        try:
            with st.spinner("Training in progress..."):
                trainer = ModelTrainer(
                    csv_path=active_dataset_path,
                    target="Fraud_Label",
                    test_size=0.2,
                )

                results, best_name = trainer.train_and_evaluate()

        except Exception as exc:
            st.error(f"Training failed: {exc}")
            return

        st.success("Training completed successfully.")

        reports_dir = os.path.join(
            project_root,
            "reports",
        )
        os.makedirs(reports_dir, exist_ok=True)

        best_metrics = results[best_name]

        report = {
            "model_name": best_name,
            "training_timestamp": datetime.now().isoformat(),
            "dataset_path": active_dataset_path,
            "metrics": best_metrics,
        }

        report_path = os.path.join(
            reports_dir,
            f"model_report_{int(time.time())}.json",
        )

        with open(report_path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        st.subheader("Training Summary")

        metric1, metric2, metric3, metric4, metric5 = st.columns(5)

        metric1.metric(
            "Accuracy",
            f"{report['metrics']['accuracy']:.1%}",
        )
        metric2.metric(
            "Precision",
            f"{report['metrics']['precision']:.1%}",
        )
        metric3.metric(
            "Recall",
            f"{report['metrics']['recall']:.1%}",
        )
        metric4.metric(
            "F1 Score",
            f"{report['metrics']['f1_score']:.1%}",
        )
        metric5.metric(
            "ROC-AUC",
            f"{report['metrics']['roc_auc']:.1%}",
        )

        st.markdown("### Model Information")

        col1, col2 = st.columns(2)

        col1.metric(
            "Best Model",
            report["model_name"],
        )

        col2.metric(
            "Report Saved",
            "Yes",
        )

        st.info(
            f"Dataset used: {report['dataset_path']}"
        )

        with st.expander("Technical report details"):
            st.code(
                json.dumps(report, indent=4),
                language="json",
            )


if __name__ == "__main__":
    render_train()