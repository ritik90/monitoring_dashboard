# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Function to calculate the percentage of failures
def get_percentage_of_failures(df, channel, no_of_days):
    # Filter the DataFrame based on the specified conditions
    filtered_df = df[
        (df['model_name'] == channel) &
        ((df['run_date'].dt.date) >= (datetime.today().date() - timedelta(days=no_of_days))) &
        (df['run_state'] != 'SUCCESS')
    ]

    # Calculate the percentage of failures
    total_records = len(df[df['model_name'] == channel])
    perc_of_failures = round(len(filtered_df) / total_records * 100, 4) if total_records > 0 else None

    return perc_of_failures

# Function to calculate the average percentage of failures
def calculate_average(df, channel, no_of_days):
    # Calculate the average percentage of failures for the given number of days
    total_percentage = 0

    for day in range(no_of_days):
        total_percentage += get_percentage_of_failures(df, channel, day + 1) or 0

    average_percentage = total_percentage / no_of_days if no_of_days > 0 else None

    return average_percentage

# Function to calculate percentages for specified timeframes
def calculate_percentages_for_timeframes(df, channel, timeframes):
    results = {}

    for days in timeframes:
        if days == 1:
            label = "Day"
        else:
            label = "Days"

        percentage_failures = get_percentage_of_failures(df, channel, days)

        if percentage_failures is not None:
            results[f"Last {days} {label}"] = percentage_failures
        else:
            results[f"Last {days} {label}"] = f"No data found in the specified timeframe."

    return results

# Function to calculate EMS Run Status for specified timeframes
def calculate_ems_run_status(df, channel, timeframes):
    results = {}

    for days in timeframes:
        if days == 1:
            label = "Day"
        else:
            label = "Days"

        # Filter the DataFrame based on the specified conditions for EMS Run Status
        filtered_df = df[
            (df['model_name'] == 'write_to_ems') &
            ((df['run_date'].dt.date) >= (datetime.today().date() - timedelta(days=days))) &
            (df['run_state'] != 'SUCCESS')
        ]

        # Calculate the percentage of successful runs (EMS Run Status)
        total_records = len(df[df['model_name'] == 'write_to_ems'])
        perc_of_success = round((len(filtered_df) / days) * 100, 4) if total_records > 0 else None

        results[f"Last {days} {label}"] = perc_of_success

    return results

# Function to calculate Same-Day FWP Rate for Follow-ups
def calculate_same_day_fwp_rate(df, channel, timeframes):
    results = {}

    for days in timeframes:
        if days == 1:
            label = "Day"
        else:
            label = "Days"

        # Filter the DataFrame for same-day follow-ups in the last n days
        filtered_df = df[
            (df['channel'] == channel) &
            (df['enq_dt'] >= (datetime.today() - timedelta(days=days))) &
            (df['cat_to_use'].isin(['HOT', 'WARM', 'COLD']))
        ]

        # Calculate same-day follow-up rate for each category
        result = filtered_df.groupby('cat_to_use')['flwup1_flag'].mean().mul(100).round(2).reset_index()

        # Order the result based on category
        result['order'] = result['cat_to_use'].map({'HOT': 1, 'WARM': 2, 'COLD': 3})
        result = result.sort_values(by='order').drop(columns='order')

        results[f"Last {days} {label}"] = result

    return results

# Function to calculate Overall FWP Rate for Follow-ups
def calculate_overall_fwp_rate(df, channel, timeframes):
    results = {}

    for days in timeframes:
        if days == 1:
            label = "Day"
        else:
            label = "Days"

        # Filter the DataFrame for overall follow-ups in the last n days
        filtered_df = df[
            (df['channel'] == channel) &
            (df['enq_dt'] >= (datetime.today() - timedelta(days=days))) &
            (df['cat_to_use'].isin(['HOT', 'WARM', 'COLD']))
        ]

        # Calculate overall follow-up rate for each category
        result = filtered_df.groupby('cat_to_use')['followed_up'].mean().mul(100).round(2).reset_index()

        # Order the result based on category
        result['order'] = result['cat_to_use'].map({'HOT': 1, 'WARM': 2, 'COLD': 3})
        result = result.sort_values(by='order').drop(columns='order')

        results[f"Last {days} {label}"] = result

    return results

# Function to calculate Same-Day FWP Rate for Follow-ups by Dealer
def calculate_same_day_fwp_rate_dealer(df, channel, timeframes):
    results = {}

    for days in timeframes:
        if days == 1:
            label = "Day"
        else:
            label = "Days"

        # Filter the DataFrame for same-day follow-ups in the last n days
        filtered_df = df[
            (df['channel'] == channel) &
            (df['enq_dt'] >= (datetime.today() - timedelta(days=days))) &
            (df['dealer_type'].isin(['AD', 'AMD']))
        ]

        # Calculate same-day follow-up rate for each category
        result = df.groupby('dealer_type')['flwup1_flag'].mean().mul(100).round(2).reset_index()

        # Order the result based on category
        result['order'] = result['dealer_type'].map({'AD': 1, 'AMD': 2})
        result = result.sort_values(by='order').drop(columns='order')

        results[f"Last {days} {label}"] = result

    return results

# Function to calculate Overall FWP Rate for Follow-ups by Dealer
def calculate_overall_fwp_rate_dealer(df, channel, timeframes):
    results = {}

    for days in timeframes:
        if days == 1:
            label = "Day"
        else:
            label = "Days"

        # Filter the DataFrame for overall follow-ups in the last n days
        filtered_df = df[
            (df['channel'] == channel) &
            (df['enq_dt'] >= (datetime.today() - timedelta(days=days))) &
            (df['dealer_type'].isin(['AD', 'AMD']))
        ]

        # Calculate overall follow-up rate for each category
        result = filtered_df.groupby('dealer_type')['followed_up'].mean().mul(100).round(2).reset_index()

        # Order the result based on category
        result['order'] = result['dealer_type'].map({'AD': 1, 'AMD': 2})
        result = result.sort_values(by='order').drop(columns='order')

        results[f"Last {days} {label})"] = result

    return results

# Function to create Hot Warm Cold Distribution plot
def create_hot_warm_cold_distribution_plot(df):
    # Create Plotly Figure
    fig = go.Figure()

    # Add traces for each category
    fig.add_trace(
        go.Scatter(
            x=df["scored_at"],
            y=df["test_cold_per"],
            name="cold_perc",
            mode="lines+markers"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["scored_at"],
            y=df["test_hot_per"],
            name="hot_perc",
            mode="lines+markers"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["scored_at"],
            y=df["test_warm_per"],
            name="warm_perc",
            mode="lines+markers"
        )
    )

    # Update layout
    fig.update_layout(title='Hot Warm Cold Distribution')

    # Show the plot
    st.plotly_chart(fig)

# Main function
def main():
    # Specify timeframes
    timeframes = [3, 7, 30]
    
    st.title("System Monitoring Dashboard")

    # Allow the user to upload separate CSV files for Pipeline Failures (EMS Write Status), Follow-ups, and Hot Warm Cold Distribution
    uploaded_file_failures = st.file_uploader("Upload CSV file for Pipeline Failures and EMS Write Status", type=["csv"])
    uploaded_file_followups = st.file_uploader("Upload CSV file for Follow-ups", type=["csv"])
    uploaded_file_hwc = st.file_uploader("Upload CSV file for Hot Warm Cold distribution", type=["csv"])

    # Check if Pipeline Failures (EMS Write Status) table is provided
    if uploaded_file_failures is not None:
        # Read the uploaded CSV file into a Pandas DataFrame
        input_df_failures = pd.read_csv(uploaded_file_failures)
        input_df_failures['run_date'] = pd.to_datetime(input_df_failures['run_date'])

        # Display the input table
        st.subheader("Input Table for Pipeline Failures and EMS Write Status:")
        st.write(input_df_failures)

        # Get distinct values from the 'model_name' column for Pipeline Failures (EMS Write Status)
        model_names_failures = input_df_failures['model_name'].unique()

        # Allow the user to select a model for Pipeline Failures (EMS Write Status)
        selected_model_failures = st.selectbox("Select Model Name for Pipeline Failures and EMS Write Status:", model_names_failures)


        # Calculate and display the percentage of failures for Pipeline Failures (EMS Write Status)
        if st.button("Calculate Percentage of Failures for Pipeline Failures"):
            results_failures = calculate_percentages_for_timeframes(input_df_failures, selected_model_failures, timeframes)

            for label, result in results_failures.items():
                st.subheader(label)
                st.write(f"### {result}")

        # Calculate and display EMS Run Status for Pipeline Failures (EMS Write Status)
        if st.button("EMS Run Status"):
            results_ems_run_status_failures = calculate_ems_run_status(input_df_failures, selected_model_failures, timeframes)

            for label, result in results_ems_run_status_failures.items():
                st.subheader(label)
                st.write(f"### {result}")

    # Check if Follow-ups table is provided
    if uploaded_file_followups is not None:
        # Read the uploaded CSV file into a Pandas DataFrame
        input_df_followups = pd.read_csv(uploaded_file_followups)
        input_df_followups['enq_dt'] = pd.to_datetime(input_df_followups['enq_dt'])

        # Map dealer_type based on dealer_id
        input_df_followups['dealer_type'] = input_df_followups['dealer_id'].apply(lambda x: 'AMD' if str(x).startswith(('1', '2', '3', '8')) else 'AD')

        # Display the input table
        st.subheader("Input Table for Follow-ups:")
        st.write(input_df_followups)

        # Get distinct values from the 'channel' column for Follow-ups
        channels_followups = input_df_followups['channel'].unique()

        # Allow the user to select a channel for Follow-ups
        selected_channel_followups = st.selectbox("Select Channel for Follow-ups:", channels_followups)

        # Calculate and display Same-Day FWP Rate for Follow-ups
        if st.button("Same-Day Followup Rate"):
            results_same_day_fwp = calculate_same_day_fwp_rate(input_df_followups, selected_channel_followups, timeframes)

            st.subheader("Same-Day Followup Rate - Hot/Warm/Cold")
            st.write(results_same_day_fwp)

            results_same_day_fwp_dealer = calculate_same_day_fwp_rate_dealer(input_df_followups, selected_channel_followups, timeframes)

            st.subheader("Same-Day Followup Rate - AD/AMD")
            st.write(results_same_day_fwp_dealer)

        # Calculate and display Overall FWP Rate for Follow-ups
        if st.button("Overall Followup Rate"):
            results_overall_fwp = calculate_overall_fwp_rate(input_df_followups, selected_channel_followups, timeframes)

            st.subheader("Overall Followup Rate - Hot/Warm/Cold")
            st.write(results_overall_fwp)

            results_overall_fwp_dealer = calculate_overall_fwp_rate_dealer(input_df_followups, selected_channel_followups, timeframes)

            st.subheader("Overall Followup Rate - AD/AMD")
            st.write(results_overall_fwp_dealer)

    # Check if Hot Warm Cold Distribution table is provided
    if uploaded_file_hwc is not None:
        # Read the uploaded CSV file into a Pandas DataFrame
        input_df_hwc = pd.read_csv(uploaded_file_hwc)
        input_df_hwc['scored_at'] = pd.to_datetime(input_df_hwc['scored_at'])

        # Display the input table
        st.subheader("Input Table for Hot Warm Cold distribution:")
        st.write(input_df_hwc)

        # Display Hot Warm Cold Distribution plot
        if st.button("Hot Warm Cold Distribution (Last 30 Days)"):
            create_hot_warm_cold_distribution_plot(input_df_hwc)

    else:
        st.warning("Please upload valid CSV files for the corresponding tables.")

# Run the main function
if __name__ == "__main__":
    main()
