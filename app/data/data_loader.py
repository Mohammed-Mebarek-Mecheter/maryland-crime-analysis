import pandas as pd

def load_data(filepath='cleaned_MD_Crime_Data.csv'):
    """
    Load data from a CSV file.
    :param filepath: Path to the CSV file.
    :return: DataFrame with the loaded data.
    """
    try:
        df = pd.read_csv(filepath)
        df = preprocess_data(df)
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return pd.DataFrame()

def preprocess_data(df):
    """
    Preprocess the data by handling missing values, and converting data types if necessary.
    :param df: DataFrame to preprocess.
    :return: Preprocessed DataFrame.
    """
    # Example preprocessing steps
    df = df.dropna()  # Drop rows with missing values
    df['Year'] = df['Year'].astype(int)  # Ensure 'Year' column is of integer type
    df = df.apply(pd.to_numeric, errors='ignore')  # Convert numeric columns to appropriate data types
    return df
