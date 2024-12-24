import streamlit as st
import pandas as pd
import random
from io import BytesIO

def main():
    st.title("ML Audit")

    # File upload
    uploaded_file = st.file_uploader("Upload Excel File", type="xlsx")

    # Initialize default criteria
    default_criteria = {
        "AUTOCODING ETAILER MATCHING": {"B&M": 0, "Amazon": 800, "Ecom": 0},
        "AUTOCODING TO RECEIPT SCHEMA FOR RECEIPT DATA": {"B&M": 1200, "Amazon": 400, "Ecom": 400},
        "AUTOCODE TO PREDICTED CI (GENAI)": {"B&M": 300, "Amazon": 0, "Ecom": 0},
        "UPC MATCHING FOR RECEIPT DATA": {"B&M": 150, "Amazon": 125, "Ecom": 50},
        "UPC MATCHING FOR DEFERRED CATEGORY": {"B&M": 150, "Amazon": 125, "Ecom": 50},
        "RCT MATCHING AUTOCODING WITHIN CODE TYPE AND PG": {"B&M": 750, "Amazon": 500, "Ecom": 250},
    }

    # Display current criteria and allow user modifications
    st.subheader(f"CRITERIA")
    user_criteria = {}

    for change_type, retailer_counts in default_criteria.items():
        st.write(f"###### {change_type}")
        columns = st.columns(len(retailer_counts))  # Create a column for each retailer
        user_criteria[change_type] = {}

        for idx, (retailer, default_count) in enumerate(retailer_counts.items()):
            with columns[idx]:  # Place each input in its respective column
                user_count = st.number_input(
                    f"{retailer}",
                    min_value=0,
                    value=default_count,
                    step=10,
                    key=f"{change_type}_{retailer}",
                )
                user_criteria[change_type][retailer] = user_count

    if uploaded_file:
        # Load the file
        df = pd.read_excel(uploaded_file)

        # Classification and Sampling
        df['Retailer'] = df['Processing Group Description'].apply(classify_retailer)
        audit_samples, summary = process_data(df, user_criteria)

        # Display audit samples and summary
        st.write("Audit Samples:")
        st.dataframe(audit_samples)

        st.write("Summary:")
        st.dataframe(summary)

        # Download the audit samples
        audit_samples_file = BytesIO()
        audit_samples.to_excel(audit_samples_file, index=False, engine="openpyxl")
        audit_samples_file.seek(0)
        st.download_button(
            label="Download Audit Samples",
            data=audit_samples_file,
            file_name="audit_samples.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Download the summary
        summary_file = BytesIO()
        summary.to_excel(summary_file, index=False, engine="openpyxl")
        summary_file.seek(0)
        st.download_button(
            label="Download Summary",
            data=summary_file,
            file_name="summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def classify_retailer(description):
    description = str(description).lower()
    if "npd amazon (us)" in description:
        return "Amazon"
    elif ".com" in description:
        return "Ecom"
    else:
        return "B&M"


def process_data(df, criteria):
    audit_samples = pd.DataFrame()
    summary = []

    for change_type, retailer_counts in criteria.items():
        for retailer, count in retailer_counts.items():
            filtered_data = df[
                (df['Changed Using'] == change_type) & (df['Retailer'] == retailer)
            ]
            actual_count = min(count, len(filtered_data))
            sampled_data = filtered_data.sample(n=actual_count, random_state=42)
            audit_samples = pd.concat([audit_samples, sampled_data])
            summary.append({
                "Changed Using": change_type,
                "Retailer": retailer,
                "Expected": count,
                "Actual": actual_count
            })

    summary_df = pd.DataFrame(summary)
    totals = pd.DataFrame({
        "Changed Using": ["Total"],
        "Retailer": ["All"],
        "Expected": [summary_df['Expected'].sum()],
        "Actual": [summary_df['Actual'].sum()]
    })
    summary_df = pd.concat([summary_df, totals], ignore_index=True)

    return audit_samples, summary_df


if __name__ == "__main__":
    main()
