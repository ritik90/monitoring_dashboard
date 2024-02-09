import streamlit as st
import pandas as pd
from pandas.api.types import CategoricalDtype

def main():
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

if __name__ == "__main__":
    main()
