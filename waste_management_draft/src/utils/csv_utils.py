# src/utils/csv_utils.py
# Common CSV processing utility functions to handle data storage uniformly

import csv
import os

def ensure_directory(file_path):
    """Ensures that the directory for the given file path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def read_csv(file_path, as_dict=True):
    """
    Reads a CSV file and returns its rows.
    
    Args:
        file_path (str): Path to the CSV file.
        as_dict (bool): If True, returns rows as dictionaries (using DictReader).
                        If False, returns rows as lists.
    """
    if not os.path.exists(file_path):
        return []
        
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as f:
            if as_dict:
                reader = csv.DictReader(f)
                return list(reader)
            else:
                reader = csv.reader(f)
                return list(reader)
    except Exception as e:
        print(f"Error reading CSV {file_path}: {e}")
        return []

def write_csv(file_path, data, headers=None, as_dict=True):
    """
    Writes or overwrites a CSV file with the provided data.
    
    Args:
        file_path (str): Path to the CSV file.
        data (list): List of rows to write (dictionaries if as_dict=True, else lists).
        headers (list): List of column names (headers). Required if as_dict=True.
        as_dict (bool): Whether data is formatted as list of dictionaries.
    """
    try:
        ensure_directory(file_path)
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            if as_dict:
                if not headers and data:
                    headers = list(data[0].keys())
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                if data:
                    writer.writerows(data)
            else:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                if data:
                    writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error writing CSV {file_path}: {e}")
        return False

def append_csv(file_path, row, headers=None, as_dict=True):
    """
    Appends a single row to a CSV file. If the file doesn't exist, writes headers first.
    
    Args:
        file_path (str): Path to the CSV file.
        row (dict or list): The row to append.
        headers (list): List of column names (headers). Required if as_dict=True.
        as_dict (bool): Whether the row is formatted as a dictionary.
    """
    try:
        ensure_directory(file_path)
        file_exists = os.path.exists(file_path)
        
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            if as_dict:
                if not headers:
                    headers = list(row.keys())
                writer = csv.DictWriter(f, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            else:
                writer = csv.writer(f)
                if not file_exists and headers:
                    writer.writerow(headers)
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error appending to CSV {file_path}: {e}")
        return False
