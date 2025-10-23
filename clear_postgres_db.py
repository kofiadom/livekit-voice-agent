#!/usr/bin/env python3
"""
Script to clear all data from the volunteers table in PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clear_volunteers_table():
    """Clear all data from volunteers table"""
    database_url = os.getenv('POSTGRES_URL_PUBLIC')
    
    if not database_url:
        print("Error: POSTGRES_URL_PUBLIC not found in .env")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Count records before deletion
        cursor.execute("SELECT COUNT(*) FROM volunteers")
        count_before = cursor.fetchone()[0]
        print(f"\nRecords before deletion: {count_before}")
        
        # Delete all records and reset the sequence
        cursor.execute("TRUNCATE TABLE volunteers RESTART IDENTITY CASCADE")
        conn.commit()
        
        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM volunteers")
        count_after = cursor.fetchone()[0]
        
        print(f"Records after deletion: {count_after}")
        print("✓ Volunteers table cleared successfully!")
        print("\nYou can now run the migration script to populate with U.S. volunteers data.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Clearing PostgreSQL Volunteers Table")
    print("="*60)
    clear_volunteers_table()