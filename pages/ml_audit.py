import streamlit as st
import pandas as pd
from io import BytesIO

# Function to classify retailers
def classify_retailer(description):
    description = str(description).lower()
    if "npd amazon (us)" in description:
        return "Amazon"
    elif ".com" in description:
        return "Ecom"
    else:
        return "B&M"

# Function to process the file
def process_file(uploaded_file):
    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(uploaded_file)

        # Step 1: Classify retailers
        df['Retailer'] = df['Processing Group Description'].apply(classify_retailer)

        # Step 2: Ensure no duplicates in External Code and Supplier Code is blank
        df = df.drop_duplicates(subset=['External Code'])
        df = df[df['Supplier Code - Current'].isnull()]

        # Step 3: Define sampling criteria
        criteria = {
            "AUTOCODING ETAILER MATCHING": {"B&M": 0, "Amazon": 800, "Ecom": 0},
            "AUTOCODING TO RECEIPT SCHEMA FOR RECEIPT DATA": {"B&M": 1200, "Amazon": 400, "Ecom": 400},
            "AUTOCODE TO PREDICTED CI (GENAI)": {"B&M": 300, "Amazon": 0, "Ecom": 0},
            "UPC MATCHING FOR RECEIPT DATA": {"B&M": 150, "Amazon": 125, "Ecom": 50},
            "UPC MATCHING FOR DEFERRED CATEGORY": {"B&M": 150, "Amazon": 125, "Ecom": 50},
            "RCT MATCHING AUTOCODING WITHIN CODE TYPE AND PG": {"B&M": 750, "Amazon": 500, "Ecom": 250},
        }

        # Step 4: Initialize DataFrame for audit samples and summary
        audit_samples = pd.DataFrame()
        summary = []

        # Step 5: Sampling process
        for change_type, retailer_counts in criteria.items():
            for retailer, count in retailer_counts.items():
                # Filter data for the specific 'Changed Using' and 'Retailer'
                filtered_data = df[(df['Changed Using'] == change_type) & (df['Retailer'] == retailer)]

                # Randomly sample the required number of rows (if available)
                actual_count = min(count, len(filtered_data))
                sampled_data = filtered_data.sample(n=actual_count, random_state=42)

                # Append the sampled data to audit_samples
                audit_samples = pd.concat([audit_samples, sampled_data])

                # Add to summary
                summary.append({
                    "Changed Using": change_type,
                    "Retailer": retailer,
                    "Expected": count,
                    "Actual": actual_count
                })

        # Step 6: Generate summary DataFrame
        summary_df = pd.DataFrame(summary)

        # Calculate the grand total for expected and actual
        totals = pd.DataFrame({
            "Changed Using": ["Total"],
            "Retailer": ["All"],
            "Expected": [summary_df['Expected'].sum()],
            "Actual": [summary_df['Actual'].sum()]
        })
        summary_df = pd.concat([summary_df, totals], ignore_index=True)

        return audit_samples, summary_df

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        return None, None

# Streamlit App
def main():
    st.title("Audit Sample Generator")
    st.write("Upload an Excel file to generate audit samples and a summary.")

    # File upload
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file:
        # Process the file
        audit_samples, summary_df = process_file(uploaded_file)

        if audit_samples is not None and summary_df is not None:
            # Display the data
            st.subheader("Audit Samples")
            st.dataframe(audit_samples)

            st.subheader("Summary")
            st.dataframe(summary_df)

            # Download buttons
            audit_buffer = BytesIO()
            audit_samples.to_excel(audit_buffer, index=False, engine='openpyxl')
            audit_buffer.seek(0)

            summary_buffer = BytesIO()
            summary_df.to_excel(summary_buffer, index=False, engine='openpyxl')
            summary_buffer.seek(0)

            st.download_button(
                label="Download Audit Samples",
                data=audit_buffer,
                file_name="audit_samples.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.download_button(
                label="Download Summary",
                data=summary_buffer,
                file_name="volume_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
