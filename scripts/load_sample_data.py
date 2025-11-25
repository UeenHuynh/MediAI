"""
Load sample data into PostgreSQL database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/mimic_iv')
DATA_DIR = Path(__file__).parent.parent / "data" / "sample"


def get_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)


def load_table(conn, table_name, csv_file, schema='raw'):
    """Load CSV file into PostgreSQL table"""
    print(f"Loading {table_name}...")

    # Read CSV
    df = pd.read_csv(csv_file)

    # Prepare data
    columns = ', '.join(df.columns)
    values = [tuple(x) for x in df.values]

    # Insert data
    with conn.cursor() as cur:
        # Clear existing data
        cur.execute(f"TRUNCATE TABLE {schema}.{table_name} CASCADE")

        # Insert new data
        execute_values(
            cur,
            f"INSERT INTO {schema}.{table_name} ({columns}) VALUES %s",
            values
        )

    conn.commit()
    print(f"✓ Loaded {len(df):,} rows into {schema}.{table_name}")


def main():
    """Load all sample data"""
    print("=" * 60)
    print("Loading Sample Data into PostgreSQL")
    print("=" * 60)

    # Check if data exists
    if not DATA_DIR.exists():
        print(f"\n✗ Data directory not found: {DATA_DIR}")
        print("  Run: python scripts/generate_sample_data.py")
        return

    try:
        # Connect to database
        conn = get_connection()
        print(f"✓ Connected to database")

        # Load tables
        load_table(conn, 'patients', DATA_DIR / 'patients.csv')
        load_table(conn, 'icustays', DATA_DIR / 'icustays.csv')
        load_table(conn, 'chartevents', DATA_DIR / 'chartevents.csv')

        conn.close()

        print("\n" + "=" * 60)
        print("✓ All data loaded successfully!")
        print("=" * 60)

        print("\nNext steps:")
        print("  1. Verify data: psql -U postgres -d mimic_iv")
        print("     SELECT COUNT(*) FROM raw.patients;")
        print("  2. Run dbt transformations: dbt run")
        print("  3. Test API: http://localhost:8000/docs")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d postgres")


if __name__ == "__main__":
    main()
