import pandas as pd

def clean_and_analyze_sales_data(input_file: str, output_file: str):
    # 1. Load the raw data
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)

    # 2. Remove the summary 'Grand Total' row to prevent data duplication in statistics
    df = df[df['Order ID'] != 'Grand Total'].copy()

    # 3. Drop '_total' columns because they are redundant aggregates of the individual ship modes
    total_cols = [col for col in df.columns if col.endswith('_total')]
    df_values = df.drop(columns=total_cols)

    # 4. Melt the dataframe from a wide format to a long/tidy format
    # This turns column headers into data rows, pairing each Order ID with its respective category and sales value
    df_tidy = df_values.melt(id_vars=['Order ID'], var_name='Category', value_name='Sales')

    # 5. Drop empty records (the empty commas in the CSV become NaNs)
    df_tidy = df_tidy.dropna(subset=['Sales']).copy()

    # 6. Parse the 'Category' column into distinct 'Segment' and 'Ship Mode' features
    # Example: 'consumer_first_class' splits into 'consumer' and 'first_class'
    df_tidy[['Segment', 'Ship Mode']] = df_tidy['Category'].str.split('_', n=1, expand=True)

    # 7. Standardize string formatting for readability
    df_tidy['Segment'] = df_tidy['Segment'].str.title()
    df_tidy['Ship Mode'] = df_tidy['Ship Mode'].str.replace('_', ' ').str.title()

    # 8. Reorder columns and drop the raw Category column
    df_cleaned = df_tidy[['Order ID', 'Segment', 'Ship Mode', 'Sales']].sort_values('Order ID')

    # 9. Calculate summary statistics based on the cleaned data
    print("\n--- Summary Statistics by Segment ---")
    segment_stats = df_cleaned.groupby('Segment')['Sales'].agg(
        Order_Count='count',
        Total_Sales='sum',
        Average_Order_Value='mean',
        Max_Order_Value='max'
    ).round(2)
    print(segment_stats)

    print("\n--- Summary Statistics by Ship Mode ---")
    ship_mode_stats = df_cleaned.groupby('Ship Mode')['Sales'].agg(
        Order_Count='count',
        Total_Sales='sum',
        Average_Order_Value='mean'
    ).round(2)
    print(ship_mode_stats)

    # 10. Export the cleaned dataset to a new CSV
    df_cleaned.to_csv(output_file, index=False)
    print(f"\nClean data successfully saved to {output_file}")

if __name__ == "__main__":
    clean_and_analyze_sales_data('raw_data.csv', 'cleaned_sales_data.csv')