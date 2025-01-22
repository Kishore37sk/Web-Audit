import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
 
# Set up auto-refresh
refresh_interval = 30  # seconds
st_autorefresh(interval=refresh_interval * 1000, key="data_refresh")
 
# Analysis Function
def consolidate_and_analyze(input_folder, user_date):
    # Initialize summaries
    folder_summary = []
    folder_auditor_summary = []
 
    for root, dirs, files in os.walk(input_folder):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
 
            # Initialize folder-level counts
            folder_completed = 0
            folder_pending = 0
            folder_total_coding_time = 0
 
            # Iterate through each file in the folder
            folder_data = []
            for file in os.listdir(folder_path):
                if file.endswith(".xlsm"):
                    file_path = os.path.join(folder_path, file)
 
                    # Read the Excel file
                    df = pd.read_excel(file_path)
 
                    # Handle the Date column
                    if 'Date' in df.columns or 'DATE' in df.columns:
                        date_col = 'Date' if 'Date' in df.columns else 'DATE'
                        df['Date'] = df[date_col]
                    else:
                        df['Date'] = pd.NaT  # If no Date column exists, set as NaN
 
                    # Replace blank or NaN dates with today's date
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').fillna(pd.Timestamp.today().normalize())
 
                    # Filter rows to include only the selected date
                    df = df[df['Date'] == pd.Timestamp(user_date).normalize()]
 
                    # If no rows match the date, skip this file
                    if df.empty:
                        continue
 
                    # Ensure START TIME and END TIME are in proper format
                    def format_time(value):
                        if pd.isna(value):
                            return "00.00.00"
                        hours = int(value * 24)
                        minutes = int((value * 24 * 60) % 60)
                        seconds = int((value * 24 * 3600) % 60)
                        return f"{hours:02}:{minutes:02}:{seconds:02}"
 
                    df['START TIME'] = df['START TIME'].apply(format_time)
                    df['END TIME'] = df['END TIME'].apply(format_time)
 
                    # Calculate coding time
                    def calculate_coding_time(row):
                        try:
                            start = pd.to_timedelta(row['START TIME'].replace('.', ':'), errors='coerce')
                            end = pd.to_timedelta(row['END TIME'].replace('.', ':'), errors='coerce')
                            coding_time = (end - start).total_seconds()
                            return max(coding_time, 0)  # Ensure no negative values
                        except:
                            return 0
 
                    df['Coding Time (seconds)'] = df.apply(calculate_coding_time, axis=1)
 
                    # Mark Auditor's Status
                    df['Auditor\'s Status'] = df['Auditor\'s Status'].fillna('Pending')
                    df['Auditor\'s Status'] = df['Auditor\'s Status'].apply(lambda x: 'Completed' if x != 'Pending' else 'Pending')
 
                    # Standardize Name column
                    if 'Name' not in df.columns and 'NAME' in df.columns:
                        df.rename(columns={'NAME': 'Name'}, inplace=True)
 
                    # Append to folder data
                    folder_data.append(df)
 
                    # Update folder-level counts
                    folder_completed += (df['Auditor\'s Status'] == 'Completed').sum()
                    folder_pending += (df['Auditor\'s Status'] == 'Pending').sum()
                    folder_total_coding_time += df['Coding Time (seconds)'].sum()
 
            # If no data for the folder matches the date, skip it
            if not folder_data:
                continue
 
            # Combine all data for the folder
            folder_df = pd.concat(folder_data, ignore_index=True)
 
            # Folder-Wise Summary
            folder_summary.append({
                'Folder': folder,
                'Completed_Count': folder_completed,
                'Pending_Count': folder_pending,
                'Total': folder_completed + folder_pending,
                'Total_Coding_Time': folder_total_coding_time
            })
 
            # Folder with Auditor-Wise Summary
            auditor_df = folder_df.groupby('Name').agg(
                Completed_Count=('Auditor\'s Status', lambda x: (x == 'Completed').sum()),
                Pending_Count=('Auditor\'s Status', lambda x: (x == 'Pending').sum()),
                Total_Coding_Time=('Coding Time (seconds)', 'sum')
            ).reset_index()
 
            auditor_df['Total'] = auditor_df['Completed_Count'] + auditor_df['Pending_Count']
            auditor_df['Folder'] = folder
            folder_auditor_summary.append(auditor_df)
 
    # Folder-Wise Summary DataFrame
    folder_summary_df = pd.DataFrame(folder_summary)
 
    # Folder with Auditor-Wise Summary DataFrame
    folder_auditor_summary_df = pd.concat(folder_auditor_summary, ignore_index=True)
 
    # Auditor-Wise Summary (aggregate across all folders)
    auditor_summary_df = folder_auditor_summary_df.groupby('Name').agg(
        Completed_Count=('Completed_Count', 'sum'),
        Pending_Count=('Pending_Count', 'sum'),
        Total_Coding_Time=('Total_Coding_Time', 'sum'),
        Total=('Total', 'sum')
    ).reset_index()
 
    # Add Grand Totals
    def add_grand_totals(df):
        grand_totals = {
            'Folder': 'Grand Totals' if 'Folder' in df.columns else None,
            'Name': 'Grand Totals' if 'Name' in df.columns else None,
            'Completed_Count': df['Completed_Count'].sum(),
            'Pending_Count': df['Pending_Count'].sum(),
            'Total': df['Total'].sum(),
            'Total_Coding_Time': df['Total_Coding_Time'].sum()
        }
        return pd.concat([df, pd.DataFrame([grand_totals])], ignore_index=True)
 
    folder_summary_df = add_grand_totals(folder_summary_df)
    folder_auditor_summary_df = add_grand_totals(folder_auditor_summary_df)
    auditor_summary_df = add_grand_totals(auditor_summary_df)
 
    # Convert Total_Coding_Time from seconds to HH:MM:SS format
    def seconds_to_hms(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
 
    folder_summary_df['Total_Coding_Time'] = folder_summary_df['Total_Coding_Time'].apply(seconds_to_hms)
    folder_auditor_summary_df['Total_Coding_Time'] = folder_auditor_summary_df['Total_Coding_Time'].apply(seconds_to_hms)
    auditor_summary_df['Total_Coding_Time'] = auditor_summary_df['Total_Coding_Time'].apply(seconds_to_hms)
 
    return folder_summary_df, auditor_summary_df, folder_auditor_summary_df
 
# Streamlit app
st.title("Summary Analysis: Folder, Auditor, and Combined")
 
# Input folder selection
input_folder = st.text_input("Enter the path of the input folder:")
user_date = st.date_input("Select a date for analysis:", value=pd.Timestamp.today())
 
if input_folder:
    folder_summary, auditor_summary, folder_auditor_summary = consolidate_and_analyze(input_folder, user_date)
 
    # Display Folder-Wise Summary
    st.subheader("Folder-Wise Summary")
    st.dataframe(folder_summary)
 
    # Display Auditor-Wise Summary
    st.subheader("Auditor-Wise Summary")
    st.dataframe(auditor_summary)
 
    # Display Folder with Auditor-Wise Summary
    st.subheader("Folder with Auditor-Wise Summary")
    st.dataframe(folder_auditor_summary)