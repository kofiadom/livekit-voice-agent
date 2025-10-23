#!/usr/bin/env python3
"""
Script to view volunteers data in PostgreSQL database
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def view_volunteers():
    """View all volunteers in PostgreSQL database"""
    database_url = os.getenv('POSTGRES_URL_PUBLIC')
    
    if not database_url:
        print("Error: POSTGRES_URL_PUBLIC not found in .env")
        return
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all volunteers
        cursor.execute("""
            SELECT id, name, age, location, phone, email, 
                   availability_status, experience_years, languages, transportation
            FROM volunteers 
            ORDER BY id
        """)
        
        volunteers = cursor.fetchall()
        
        print("\n" + "="*80)
        print(f"Total Volunteers in PostgreSQL Database: {len(volunteers)}")
        print("="*80 + "\n")
        
        for vol in volunteers:
            print(f"ID: {vol['id']}")
            print(f"Name: {vol['name']}")
            print(f"Age: {vol['age']}")
            print(f"Location: {vol['location']}")
            print(f"Phone: {vol['phone']}")
            print(f"Email: {vol['email']}")
            print(f"Status: {vol['availability_status']}")
            print(f"Experience: {vol['experience_years']} years")
            print(f"Languages: {vol['languages']}")
            print(f"Transportation: {vol['transportation']}")
            print("-" * 80)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_volunteers()