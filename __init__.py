import streamlit as st
from streamlit_option_menu import option_menu
# import model_monitoring_app, system_monitoring_app, business_monitoring_app
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from pandas.api.types import CategoricalDtype

def run_all():

    st.set_page_config(page_title="Monitoring")

    class MultiApp:

        def __init__(self):
            self.apps = []

        def add_app(self, title, func):
            self.apps.append({
                "title": title,
                "function": func
            })

        def run(self):

            st.markdown(
                """
                <style>
                    .sidebar .sidebar-content {
                        padding-top: 5px;
                    }
                    .sidebar .sidebar-content .sidebar-collapse h1 {
                        font-size: 28px;
                        margin-bottom: 20px;
                    }
                    .sidebar .sidebar-content img {
                        width: 5px;
                        margin-bottom: 5px;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Add your custom logo with the absolute path
            st.sidebar.image("/Users/ritik.saxena/Documents/image.jpg")

            st.sidebar.header("Monitoring Dashboard")
            app_selection = st.sidebar.selectbox(
                "Select Monitoring Type",
                ('Model Monitoring', 'System Monitoring', 'Business Monitoring'),
                index=1
            )

            if app_selection == "Model Monitoring":

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

                def model_monitoring():

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

                # if __name__ == "__main__":
                model_monitoring()

            elif app_selection == "System Monitoring":
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
                def system_monitoring():
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
                # if __name__ == "__main__":
                system_monitoring()

            elif app_selection == "Business Monitoring":
                def business_monitoring():
                    st.title("Business Monitoring Dashbaord")

                    # File upload
                    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

                    if uploaded_file is not None:
                        # Read CSV data
                        df_streamlit = pd.read_csv(uploaded_file)

                        # Display the DataFrame
                        st.write("Preview of the uploaded data:")
                        st.dataframe(df_streamlit)

                        # Additional Streamlit widgets for filters
                        start_date = st.date_input("Start Date", pd.to_datetime('today') - pd.to_timedelta(7, 'd'))
                        end_date = st.date_input("End Date", pd.to_datetime('today'))

                        # Widgets for Enquiry Categories
                        cat_to_use = "HOT,WARM,COLD"
                        cat_to_use_list = cat_to_use.split(',')
                        cat_to_use_list_str = str(cat_to_use_list)

                        # Ordering DF in a given specific order
                        cat_label_order = CategoricalDtype(["HOT", "WARM", "COLD"], ordered=True)

                        # Convert 'enq_dt' column to datetime
                        df_streamlit['enq_dt'] = pd.to_datetime(df_streamlit['enq_dt'])

                        # Convert the date input to datetime
                        start_date = pd.to_datetime(start_date)
                        end_date = pd.to_datetime(end_date)

                        # Apply necessary filters for Query 1
                        filtered_data1 = df_streamlit[
                            (df_streamlit['set_type'] == 'test') &
                            (df_streamlit['enq_dt'].between(start_date, end_date))
                        ]

                        # Apply additional filters if needed
                        filtered_data1 = filtered_data1[filtered_data1['rnum'] == 1]
                        filtered_data1 = filtered_data1[filtered_data1['cat_to_use'].isin(cat_to_use_list)]

                        # Calculate required metrics for Query 1
                        df1 = (
                            filtered_data1.groupby('cat_to_use')
                            .agg(
                                label=('cat_to_use', 'first'),
                                total_enqs=('enq_key', 'nunique'),
                                flwup_total=('enq_key', lambda x: x[filtered_data1['followed_up'] >= 1].nunique()),
                                flwup1_per=('enq_key', lambda x: x[filtered_data1['flwup1_flag'] == 1].nunique() / x.nunique() * 100),
                                flwup_rtl_per=('retail_dar', lambda x: (x.sum() / x[filtered_data1['followed_up'] >= 1].sum()) * 100),
                                retail_total=('retail_dar', 'sum')
                            )
                            .reset_index(drop=True)
                        )

                        # Additional calculations and data processing for Query 1
                        df1['retail_per'] = (df1['retail_total'] / df1['total_enqs']) * 100
                        df1['label'] = df1['label'].astype(cat_label_order)

                        df1 = df1.sort_values('label').reset_index(drop=True)

                        df1['exp_enq'] = "-"
                        df1['exp_flwup'] = "-"
                        df1['exp_retail'] = "-"
                        df1['enq_dist'] = (df1['total_enqs'] / df1['total_enqs'].sum() * 100).round(2)
                        df1['retail_dist'] = (df1['retail_total'] / df1['retail_total'].sum() * 100).round(2)

                        # Define the desired columns for display for Query 1
                        req_columns1 = [
                            "label",
                            "total_enqs",
                            "enq_dist",
                            "flwup1_per",
                            "retail_total",
                            "retail_dist",
                            "retail_per"
                        ]

                        df1 = df1[req_columns1]
                        df1.columns = ["Enquiry Category", "# Enquiries", "Actual Enquriy Distribution", "% 1 day followup Actual", "# Retails", "% Retails Actual", "% Retail / Enquiry"]

                        # Display the resulting DataFrame for Query 1
                        st.subheader("Hot Warm Cold Distribution")
                        # st.text(f"Using Enquiry Categories: {cat_to_use_list_str}")
                        st.dataframe(df1)

                        # Apply necessary filters for Query 2
                        filtered_data2 = df_streamlit[
                            (df_streamlit['enq_dt'].between(start_date, end_date)) 
                        ]

                        # Apply additional filters if needed for Query 2
                        filtered_data2 = filtered_data2[filtered_data2['rnum'] == 1]
                        filtered_data2 = filtered_data2[filtered_data2['cat_to_use'].isin(cat_to_use_list)]

                        # Calculate required metrics for Query 2
                        df2 = (
                            filtered_data2.groupby('set_type')
                            .agg(
                                label=('set_type', 'first'),
                                total_enqs=('enq_key', 'nunique'),
                                flwup_total=('enq_key', lambda x: x[filtered_data2['followed_up'] >= 1].nunique()),
                                flwup1_per=('enq_key', lambda x: x[filtered_data2['flwup1_flag'] == 1].nunique() / x.nunique() * 100),
                                flwup_rtl_per=('retail_dar', lambda x: (x.sum() / x[filtered_data2['followed_up'] >= 1].sum()) * 100),
                                retail_total=('retail_dar', 'sum')
                            )
                            .reset_index(drop=True)
                        )

                        # Additional calculations and data processing for Query 2
                        df2['retail_per'] = (df2['retail_total'] / df2['total_enqs']) * 100

                        df2 = df2.sort_values('label').reset_index(drop=True)

                        df2['exp_enq'] = "-"
                        df2['exp_flwup'] = "-"
                        df2['exp_retail'] = "-"
                        df2['enq_dist'] = (df2['total_enqs'] / df2['total_enqs'].sum() * 100).round(2)
                        df2['retail_dist'] = (df2['retail_total'] / df2['retail_total'].sum() * 100).round(2)

                        # Define the desired columns for display for Query 2
                        req_columns2 = [
                            "label",
                            "total_enqs",
                            "enq_dist",
                            "flwup1_per",
                            "retail_total",
                            "retail_dist",
                            "retail_per"
                        ]

                        df2 = df2[req_columns2]
                        df2.columns = ["Set", "# Enquiries", "Actual Enquriy Distribution", "% 1 day followup Actual", "# Retails", "% Retails Actual", "% Retail / Enquiry"]

                        # Display the resulting DataFrame for Query 2
                        st.subheader("Test vs Control Distribution")
                        # st.text(f"Using Enquiry Categories: {cat_to_use_list_str}")
                        st.dataframe(df2)

                # if __name__ == "__main__":
                business_monitoring()

    multi_app = MultiApp()
    multi_app.run()

def main():
    run_all()

if __name__ == "__main__":
    main()
