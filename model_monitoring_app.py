# app.py
import numpy as np
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def load_and_filter_data(input_df, no_of_days):
    filtered_data = input_df[input_df['computed_on'] >= datetime.now() - timedelta(days=no_of_days)]
    return filtered_data

def calculate_average(input_df, feature, no_of_days):
    filtered_data = load_and_filter_data(input_df, no_of_days)
    return filtered_data[feature].mean()

def display_results(input_df, selected_column, no_of_days):
    result_df = calculate_average(input_df, selected_column, no_of_days)
    result_df = round(result_df, 2)

    st.subheader(f"{selected_column.title()} (Last 3 Days)")
    st.write(f"### {result_df}")

    st.subheader(f"{selected_column.title()} ( Last 7 Days)")
    st.write(f"### {calculate_average(input_df, selected_column, 6)}")

    st.subheader(f"{selected_column.title()} (Last 30 Days)")
    input_df_plot = load_and_filter_data(input_df, 29)
    st.line_chart(data=input_df_plot, x='computed_on', y=selected_column)

def calculate_abnormality(input_df, selected_columns, no_of_days):

    filtered_data = input_df[(input_df['computed_on'] >= datetime.now() - timedelta(days=no_of_days)) & (input_df[selected_columns] > 0)]

    # Calculate the number of abnormalities
    no_of_abnormalities = filtered_data[selected_columns].count()

    # Use a case statement to determine abnormality
    abnormality = "True" if no_of_abnormalities > 1 else "False"
    st.subheader(f"{selected_columns} (Last 3 Days)")
    st.write(f"### {abnormality}")

    #  7 Days
    filtered_data = input_df[(input_df['computed_on'] >= datetime.now() - timedelta(days=no_of_days)) & (input_df[selected_columns] > 0)]

    # Calculate the number of abnormalities
    no_of_abnormalities = filtered_data[selected_columns].count()

    # Use a case statement to determine abnormality
    abnormality = "True" if no_of_abnormalities > 1 else "False"
    st.subheader(f"{selected_columns} ( Last 7 Days)")
    st.write(f"### {abnormality}")

    st.subheader(f"{selected_columns.title()} (Last 30 Days)")
    input_df_plot_abn = load_and_filter_data(input_df, 29)
    st.line_chart(data=input_df_plot_abn, x='computed_on', y=selected_columns)

def main():
    st.title("Model Monitoring Dashboard")

    # Allow the user to upload a CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read the uploaded CSV file into a Pandas DataFrame
        input_df = pd.read_csv(uploaded_file)
        input_df['computed_on'] = pd.to_datetime(input_df['computed_on'])

        # Display the input table
        st.subheader("Input Table:")
        st.write(input_df)

        selected_column = st.selectbox("Select a column for values", ['f2_score', 'recall_score', 'precision_score', 'ks_abn_detected', 'conv_abn_detected'])

        if selected_column in ('f2_score', 'recall_score', 'precision_score'):
            # Display results for the selected column
            display_results(input_df, selected_column, 2)

        # KS abnormality
        elif selected_column in ('ks_abn_detected', 'conv_abn_detected'):
            calculate_abnormality(input_df, selected_column, 2)

    else:
        st.warning("Please upload a valid CSV file.")

if __name__ == "__main__":
    main()
