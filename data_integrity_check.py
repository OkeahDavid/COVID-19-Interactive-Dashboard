import logging

# Setting up the logging configuration
logging.basicConfig(filename='data_update_log.log', level=logging.INFO)

def check_data_integrity(df):
    """
    Checks the integrity of the COVID-19 data DataFrame.

    Args:
    df (pandas.DataFrame): The DataFrame containing the COVID-19 data.

    Raises:
    ValueError: If the data integrity checks fail.
    """
    try:
        # Define a list of expected columns in the DataFrame
        expected_columns = ['Date_reported', 'Country', 'New_cases', 'Cumulative_cases']

        # Check if all expected columns are present in the DataFrame
        if not all(col in df.columns for col in expected_columns):
            # Raise an error if any expected column is missing
            raise ValueError("Data integrity check failed: Missing columns")
        
        # Log a message if the data passes all integrity checks
        logging.info("Data integrity check passed.")
    except Exception as e:
        # Log any exceptions that occur during the integrity check
        logging.error(f"Data integrity check failed: {e}")
        # Re-raise the exception for higher-level handling
        raise
