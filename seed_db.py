import sqlite3
import pandas as pd
import os
from datetime import datetime

# Paths
DB_FILE = "leases.db"
DATA_DIR = "data"

# Custom date parser for DD/MM/YYYY format
def parse_date(date_str):
    if pd.isna(date_str):
        return None
    return datetime.strptime(date_str, '%d/%m/%Y').date()

# Read CSVs
properties_df = pd.read_csv(os.path.join(DATA_DIR, "properties.csv"))
units_df = pd.read_csv(os.path.join(DATA_DIR, "units.csv"))
leases_df = pd.read_csv(os.path.join(DATA_DIR, "leases.csv"))

# Convert date columns
leases_df['start_date'] = leases_df['start_date'].apply(parse_date)
leases_df['end_date'] = leases_df['end_date'].apply(parse_date)

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)

# Save to tables
properties_df.to_sql("properties", conn, if_exists="replace", index=False)
units_df.to_sql("units", conn, if_exists="replace", index=False)
leases_df.to_sql("leases", conn, if_exists="replace", index=False)

print("Database created successfully.")

conn.close()
