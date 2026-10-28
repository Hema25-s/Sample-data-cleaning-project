
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------
st.set_page_config(
    page_title="CSV Data Cleaning App",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 CSV Data Cleaning Application")
st.write(
    "Upload a CSV file, clean your data, "
    "modify columns, and download the results."
)

# ----------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "original_df" not in st.session_state:
    st.session_state.original_df = None

# ----------------------------------
# FILE UPLOAD
# ----------------------------------
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    # Load only when a new file is uploaded
    if (
        "uploaded_name" not in st.session_state
        or st.session_state.uploaded_name != uploaded_file.name
    ):
        try:
            df = pd.read_csv(
                uploaded_file,
                encoding="cp1252"
            )

            st.session_state.df = df.copy()
            st.session_state.original_df = df.copy()
            st.session_state.uploaded_name = uploaded_file.name

            st.success("File loaded successfully!")

        except Exception as e:
            st.error(f"Error loading file: {e}")

# ----------------------------------
# MAIN APPLICATION
# ----------------------------------
if st.session_state.df is not None:

    df = st.session_state.df

    st.divider()

    # DATASET INFORMATION
    st.header("📊 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Rows", df.shape[0])

    with col2:
        st.metric("Total Columns", df.shape[1])

    with col3:
        st.metric("Missing Values", int(df.isnull().sum().sum()))

    with col4:
        st.metric("Duplicate Rows", int(df.duplicated().sum()))

    st.subheader("Current Dataset")
    st.dataframe(df, use_container_width=True)

    # ----------------------------------
    # SIDEBAR MENU
    # ----------------------------------
    st.sidebar.title("🛠️ Data Cleaning Menu")

    operation = st.sidebar.radio(
        "Choose an operation",
        [
            "Check Null Values",
            "Fill Null Values",
            "Remove Null Values",
            "Check Duplicates",
            "Remove Duplicates",
            "Change Data Type",
            "Merge Columns",
            "Select Data",
            "Save Clean File",
            "Reset Dataset"
        ]
    )

    # ----------------------------------
    # 1. CHECK NULL VALUES
    # ----------------------------------
    if operation == "Check Null Values":

        st.header("1. Check Null Values")

        null_counts = df.isnull().sum()

        null_table = pd.DataFrame({
            "Column": df.columns,
            "Null Count": null_counts.values,
            "Data Type": df.dtypes.astype(str).values
        })

        st.dataframe(null_table, use_container_width=True)

        total_nulls = int(null_counts.sum())

        if total_nulls > 0:
            st.warning(f"Total missing values: {total_nulls}")
        else:
            st.success("No missing values found.")

    # ----------------------------------
    # 2. FILL NULL VALUES
    # ----------------------------------
    elif operation == "Fill Null Values":

        st.header("2. Fill Null Values")

        method = st.selectbox(
            "Choose filling method",
            [
                "Forward Fill (ffill)",
                "Backward Fill (bfill)",
                "Fill with Mean/Mode",
                "Fill with Custom Value"
            ]
        )

        if method == "Fill with Custom Value":

            column = st.selectbox(
                "Select column",
                df.columns
            )

            value = st.text_input(
                "Enter replacement value"
            )

            if st.button("Fill Missing Values"):

                try:
                    if pd.api.types.is_numeric_dtype(df[column]):
                        replacement = float(value)

                        if pd.api.types.is_integer_dtype(df[column]):
                            if replacement.is_integer():
                                replacement = int(replacement)

                    else:
                        replacement = value

                    df[column] = df[column].fillna(replacement)

                    st.session_state.df = df
                    st.success("Missing values filled successfully!")

                except Exception as e:
                    st.error(f"Error: {e}")

        else:

            if st.button("Apply Filling Method"):

                if method == "Forward Fill (ffill)":
                    df = df.ffill()

                elif method == "Backward Fill (bfill)":
                    df = df.bfill()

                elif method == "Fill with Mean/Mode":

                    for column in df.columns:

                        if not df[column].isnull().any():
                            continue

                        if pd.api.types.is_numeric_dtype(df[column]):
                            mean_value = df[column].mean()

                            if pd.notna(mean_value):
                                df[column] = df[column].fillna(mean_value)

                        else:
                            mode_values = df[column].mode_
