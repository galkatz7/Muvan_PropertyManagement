import sqlite3
import pandas as pd
import os

# Paths
DB_FILE = "leases.db"
DATA_DIR = "data"

# Read CSVs
leases_df = pd.read_csv(os.path.join(DATA_DIR, "leases.csv"))
properties_df = pd.read_csv(os.path.join(DATA_DIR, "properties.csv"))
units_df = pd.read_csv(os.path.join(DATA_DIR, "units.csv"))

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)

# Save to tables
properties_df.to_sql("properties", conn, if_exists="replace", index=False)
units_df.to_sql("units", conn, if_exists="replace", index=False)
leases_df.to_sql("leases", conn, if_exists="replace", index=False)

print("Database created successfully.")

conn.close()
