import os
import gdown
import zipfile
from dotenv import load_dotenv
import os
load_dotenv()

data_path = os.getenv('DATA_PATH')  # default to 'image_data/'

def downloadFiles():
    file_id = os.getenv('FILE_ID')
    url = f'https://drive.google.com/uc?id={file_id}'
    # Ensure the directory exists
    os.makedirs(data_path, exist_ok=True)

    zip_path = os.path.join(data_path, 'downloaded_file.zip')  # saving with .zip extension

    # Download the file
    gdown.download(url, zip_path, quiet=False)
    print(f"File downloaded to: {zip_path}")

    # Unzip the downloaded file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_path)
    print(f"Extracted all files to: {data_path}")

    # Optional: Remove the zip file after extraction
    # os.remove(zip_path)
