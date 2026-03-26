import pandas as pd
from google.colab import drive

def read_excel_from_drive(file_id, sheet_name=0):
    drive.mount('/content/drive')  # Mount Google Drive
    file_path = f'/content/drive/My Drive/{file_id}'  # Path to the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)  # Read the Excel file
    return df