import requests
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(filename='data_update_log.log', level=logging.INFO)

def fetch_latest_data(url, default_data_path):
    """
    Fetches the latest COVID-19 data from the given URL and saves it to a CSV file.
    
    Args:
    url (str): URL to fetch the data from.

    Returns:
    str: The filename where the data is saved.
    """
    try:
        # Send a GET request to the server, enabling stream mode for downloading large files
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            # Get the total size of the file to be downloaded from the headers
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            chunk_size = 1024  # Set chunk size to 1 Kilobyte

            filename = 'latest_covid_data.csv'

            # Open a file to write the data to, and set up the tqdm progress bar
            with open(filename, 'wb') as file, tqdm(
                desc=filename,
                total=total_size_in_bytes,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024
            ) as bar:
                # Read the response in chunks
                for data in response.iter_content(chunk_size):
                    # Write each chunk to the file and update the progress bar
                    file.write(data)
                    bar.update(len(data))

            # Log the successful fetching of data
            logging.info("Data fetched successfully.")
            return filename
        else:
            # Raise an exception if the response status is not 200 (OK)
            raise Exception("Failed to fetch data with status code: " + str(response.status_code))
    except Exception as e:
        logging.error(f"Error occurred during data fetching: {e}")
        logging.info(f"Using default data from {default_data_path}")
        return default_data_path