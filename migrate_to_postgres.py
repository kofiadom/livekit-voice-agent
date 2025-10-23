#!/usr/bin/env python3
"""
LiveKit Voice Agent - SQLite to PostgreSQL Database Migration Script

This script migrates the volunteers database from SQLite to a PostgreSQL database hosted on Coolify.
It handles the differences between SQLite and PostgreSQL, including:
- SERIAL column handling (auto-increment)
- Boolean type conversion
- Proper connection string formatting

Usage:
    python migrate_to_postgres.py

Prerequisites:
    1. PostgreSQL database created and accessible on Coolify
    2. POSTGRES_URL_PUBLIC environment variable set in .env file
    3. Local SQLite database (volunteers.db) exists (optional)
    4. psycopg2-binary driver installed

The script will:
1. Test connection to PostgreSQL Database
2. Create volunteers table with proper PostgreSQL schema
3. Transfer all data from SQLite to PostgreSQL (if SQLite DB exists)
4. Create sample U.S. volunteers data if no SQLite data found
5. Verify the data transfer

Author: Global Health Studio Team
"""

import os
import sqlite3
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_postgres_connection():
    """Create and return a PostgreSQL connection using public URL"""
    database_url = os.getenv('POSTGRES_URL_PUBLIC')
    
    if not database_url:
        print("✗ POSTGRES_URL_PUBLIC environment variable not found!")
        print("Please make sure you have set POSTGRES_URL_PUBLIC in your .env file.")
        return None
    
    if database_url.startswith("sqlite"):
        print("✗ POSTGRES_URL_PUBLIC is still pointing to SQLite. Please update it to PostgreSQL.")
        return None
    
    if not database_url.startswith("postgresql"):
        print("✗ POSTGRES_URL_PUBLIC should start with 'postgresql://' for PostgreSQL connections.")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        # Test connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        print("✓ Successfully connected to PostgreSQL Database")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL Database: {e}")
        print("\nTo fix this issue:")
        print("1. Ensure PostgreSQL is running on Coolify")
        print("2. Check your POSTGRES_URL_PUBLIC format: postgresql://user:password@host:port/database")
        print("3. Install psycopg2: pip install psycopg2-binary")
        print("4. Verify network connectivity to your Coolify PostgreSQL instance")
        return None

def get_sqlite_connection():
    """Create and return a SQLite connection"""
    try:
        if not os.path.exists('volunteers.db'):
            print("WARNING: volunteers.db not found. Will create PostgreSQL table with sample data only.")
            return None
        conn = sqlite3.connect('volunteers.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except Exception as e:
        print(f"ERROR: Failed to connect to SQLite: {e}")
        return None

def create_postgres_table(pg_conn):
    """Create the volunteers table in PostgreSQL"""
    cursor = pg_conn.cursor()
    
    # Drop table if exists (for clean migration)
    cursor.execute("DROP TABLE IF EXISTS volunteers CASCADE;")
    
    # Create volunteers table with PostgreSQL-specific syntax
    cursor.execute('''
        CREATE TABLE volunteers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INTEGER NOT NULL,
            location VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            email VARCHAR(255),
            skills TEXT NOT NULL,  -- JSON array of skills
            availability_status VARCHAR(20) NOT NULL CHECK (availability_status IN ('available', 'busy', 'unavailable')),
            availability_schedule TEXT,  -- JSON object with schedule
            experience_years INTEGER DEFAULT 0,
            languages TEXT,  -- JSON array of languages spoken
            transportation VARCHAR(20) CHECK (transportation IN ('car', 'public_transport', 'walking', 'bicycle')),
            background_check BOOLEAN DEFAULT FALSE,
            emergency_contact TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX idx_volunteers_location ON volunteers(location);")
    cursor.execute("CREATE INDEX idx_volunteers_availability ON volunteers(availability_status);")
    cursor.execute("CREATE INDEX idx_volunteers_transportation ON volunteers(transportation);")
    cursor.execute("CREATE INDEX idx_volunteers_experience ON volunteers(experience_years);")
    
    pg_conn.commit()
    print("SUCCESS: PostgreSQL volunteers table created successfully!")

def migrate_data_from_sqlite(sqlite_conn, pg_conn):
    """Migrate data from SQLite to PostgreSQL"""
    if sqlite_conn is None:
        print("INFO: No SQLite database found, skipping data migration.")
        return 0
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Get all data from SQLite
    sqlite_cursor.execute("SELECT * FROM volunteers")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print("INFO: No data found in SQLite database.")
        return 0
    
    # Insert data into PostgreSQL
    migrated_count = 0
    for row in rows:
        try:
            pg_cursor.execute('''
                INSERT INTO volunteers (
                    name, age, location, phone, email, skills, availability_status,
                    availability_schedule, experience_years, languages, transportation,
                    background_check, emergency_contact, notes, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                row['name'], row['age'], row['location'], row['phone'], row['email'],
                row['skills'], row['availability_status'], row['availability_schedule'],
                row['experience_years'], row['languages'], row['transportation'],
                bool(row['background_check']), row['emergency_contact'], row['notes'],
                row['created_at'], row['updated_at']
            ))
            migrated_count += 1
        except Exception as e:
            print(f"ERROR: Failed to migrate record {row['name']}: {e}")
    
    pg_conn.commit()
    print(f"SUCCESS: Migrated {migrated_count} records from SQLite to PostgreSQL!")
    return migrated_count

def create_sample_data(pg_conn):
    """Create sample data if no SQLite data was migrated - using the same U.S. volunteers data"""
    cursor = pg_conn.cursor()
    
    # Sample volunteer data from various US states (same as original create_volunteers_db.py)
    volunteers_data = [
        # Massachusetts volunteers
        {
            'name': 'Sarah Johnson',
            'age': 45,
            'location': 'Worcester, MA',
            'phone': '(508) 555-0123',
            'email': 'sarah.johnson@email.com',
            'skills': json.dumps(['cooking', 'medication_reminders', 'companionship', 'light_housekeeping']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '9:00-17:00',
                'tuesday': '9:00-17:00',
                'wednesday': '9:00-17:00',
                'thursday': '9:00-17:00',
                'friday': '9:00-17:00',
                'weekend': 'flexible'
            }),
            'experience_years': 8,
            'languages': json.dumps(['English', 'Spanish']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'John Johnson - (508) 555-0124',
            'notes': 'Certified nursing assistant, specializes in elderly care'
        },
        {
            'name': 'Michael Chen',
            'age': 32,
            'location': 'Boston, MA',
            'phone': '(617) 555-0234',
            'email': 'michael.chen@email.com',
            'skills': json.dumps(['transportation', 'grocery_shopping', 'technology_help', 'companionship']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '14:00-20:00',
                'tuesday': '14:00-20:00',
                'wednesday': '14:00-20:00',
                'thursday': '14:00-20:00',
                'friday': '14:00-20:00',
                'saturday': '10:00-18:00',
                'sunday': 'unavailable'
            }),
            'experience_years': 3,
            'languages': json.dumps(['English', 'Mandarin']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Lisa Chen - (617) 555-0235',
            'notes': 'Tech specialist, great with helping seniors use smartphones and tablets'
        },
        # New York volunteers
        {
            'name': 'Maria Rodriguez',
            'age': 28,
            'location': 'Albany, NY',
            'phone': '(518) 555-0345',
            'email': 'maria.rodriguez@email.com',
            'skills': json.dumps(['physical_therapy_support', 'exercise_assistance', 'companionship', 'reading']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '8:00-16:00',
                'tuesday': '8:00-16:00',
                'wednesday': '8:00-16:00',
                'thursday': '8:00-16:00',
                'friday': '8:00-16:00',
                'saturday': '9:00-15:00',
                'sunday': '9:00-15:00'
            }),
            'experience_years': 5,
            'languages': json.dumps(['English', 'Spanish']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Carlos Rodriguez - (518) 555-0346',
            'notes': 'Physical therapy assistant, excellent for mobility and exercise support'
        },
        {
            'name': 'James Wilson',
            'age': 41,
            'location': 'Rochester, NY',
            'phone': '(585) 555-0456',
            'email': 'james.wilson@email.com',
            'skills': json.dumps(['home_maintenance', 'gardening', 'companionship', 'pet_care']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '8:00-16:00',
                'tuesday': '8:00-16:00',
                'wednesday': '8:00-16:00',
                'thursday': '8:00-16:00',
                'friday': '8:00-16:00',
                'saturday': '8:00-12:00',
                'sunday': 'flexible'
            }),
            'experience_years': 12,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Susan Wilson - (585) 555-0457',
            'notes': 'Retired contractor, loves helping with home repairs and yard work'
        },
        # Connecticut volunteers
        {
            'name': 'Jennifer Walsh',
            'age': 38,
            'location': 'Hartford, CT',
            'phone': '(860) 555-0567',
            'email': 'jennifer.walsh@email.com',
            'skills': json.dumps(['cooking', 'meal_planning', 'companionship', 'medication_reminders']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '10:00-18:00',
                'tuesday': '10:00-18:00',
                'wednesday': '10:00-18:00',
                'thursday': '10:00-18:00',
                'friday': '10:00-14:00',
                'saturday': 'flexible',
                'sunday': 'flexible'
            }),
            'experience_years': 6,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Patrick Walsh - (860) 555-0568',
            'notes': 'Professional chef, specializes in healthy meals for seniors'
        },
        {
            'name': 'Linda Davis',
            'age': 42,
            'location': 'New Haven, CT',
            'phone': '(203) 555-0678',
            'email': 'linda.davis@email.com',
            'skills': json.dumps(['healthcare_support', 'medication_management', 'companionship', 'light_housekeeping']),
            'availability_status': 'busy',
            'availability_schedule': json.dumps({
                'monday': 'unavailable',
                'tuesday': '16:00-20:00',
                'wednesday': 'unavailable',
                'thursday': '16:00-20:00',
                'friday': 'unavailable',
                'saturday': '10:00-16:00',
                'sunday': '10:00-16:00'
            }),
            'experience_years': 15,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Mark Davis - (203) 555-0679',
            'notes': 'Registered nurse, currently working part-time but available for select hours'
        },
        # Florida volunteers
        {
            'name': 'David Kim',
            'age': 29,
            'location': 'Tampa, FL',
            'phone': '(813) 555-0789',
            'email': 'david.kim@email.com',
            'skills': json.dumps(['transportation', 'errands', 'technology_help', 'companionship']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '12:00-20:00',
                'tuesday': '12:00-20:00',
                'wednesday': '12:00-20:00',
                'thursday': '12:00-20:00',
                'friday': '12:00-20:00',
                'saturday': '9:00-17:00',
                'sunday': '9:00-17:00'
            }),
            'experience_years': 2,
            'languages': json.dumps(['English', 'Korean']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Grace Kim - (813) 555-0790',
            'notes': 'College graduate, very patient and great with technology assistance'
        },
        {
            'name': 'Patricia O\'Brien',
            'age': 51,
            'location': 'Miami, FL',
            'phone': '(305) 555-0890',
            'email': 'patricia.obrien@email.com',
            'skills': json.dumps(['companionship', 'reading', 'crafts', 'light_housekeeping']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '9:00-15:00',
                'tuesday': '9:00-15:00',
                'wednesday': '9:00-15:00',
                'thursday': '9:00-15:00',
                'friday': '9:00-15:00',
                'saturday': 'flexible',
                'sunday': 'flexible'
            }),
            'experience_years': 7,
            'languages': json.dumps(['English', 'Spanish']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Sean O\'Brien - (305) 555-0891',
            'notes': 'Retired librarian, loves reading and doing crafts with seniors'
        },
        # California volunteers
        {
            'name': 'Amanda Garcia',
            'age': 35,
            'location': 'Los Angeles, CA',
            'phone': '(323) 555-0901',
            'email': 'amanda.garcia@email.com',
            'skills': json.dumps(['cooking', 'companionship', 'transportation', 'pet_care']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '10:00-18:00',
                'tuesday': '10:00-18:00',
                'wednesday': '10:00-18:00',
                'thursday': '10:00-18:00',
                'friday': '10:00-18:00',
                'saturday': '8:00-14:00',
                'sunday': 'flexible'
            }),
            'experience_years': 4,
            'languages': json.dumps(['English', 'Spanish']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Miguel Garcia - (323) 555-0902',
            'notes': 'Bilingual caregiver with experience in senior nutrition and meal prep'
        },
        {
            'name': 'Thomas Anderson',
            'age': 48,
            'location': 'San Francisco, CA',
            'phone': '(415) 555-1012',
            'email': 'thomas.anderson@email.com',
            'skills': json.dumps(['technology_help', 'companionship', 'errands', 'reading']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '14:00-20:00',
                'tuesday': '14:00-20:00',
                'wednesday': '14:00-20:00',
                'thursday': '14:00-20:00',
                'friday': '14:00-20:00',
                'saturday': '10:00-16:00',
                'sunday': 'unavailable'
            }),
            'experience_years': 6,
            'languages': json.dumps(['English']),
            'transportation': 'public_transport',
            'background_check': True,
            'emergency_contact': 'Sarah Anderson - (415) 555-1013',
            'notes': 'Former IT professional, excellent at helping seniors with computers and smartphones'
        },
        # Texas volunteers
        {
            'name': 'Rebecca Martinez',
            'age': 33,
            'location': 'Austin, TX',
            'phone': '(512) 555-1123',
            'email': 'rebecca.martinez@email.com',
            'skills': json.dumps(['physical_therapy_support', 'exercise_assistance', 'medication_reminders', 'companionship']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '8:00-16:00',
                'tuesday': '8:00-16:00',
                'wednesday': '8:00-16:00',
                'thursday': '8:00-16:00',
                'friday': '8:00-16:00',
                'saturday': '9:00-13:00',
                'sunday': 'flexible'
            }),
            'experience_years': 9,
            'languages': json.dumps(['English', 'Spanish']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Jose Martinez - (512) 555-1124',
            'notes': 'Licensed physical therapist assistant, specializes in senior mobility'
        },
        {
            'name': 'William Brown',
            'age': 56,
            'location': 'Dallas, TX',
            'phone': '(214) 555-1234',
            'email': 'william.brown@email.com',
            'skills': json.dumps(['home_maintenance', 'gardening', 'companionship', 'transportation']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '7:00-15:00',
                'tuesday': '7:00-15:00',
                'wednesday': '7:00-15:00',
                'thursday': '7:00-15:00',
                'friday': '7:00-15:00',
                'saturday': '8:00-12:00',
                'sunday': 'flexible'
            }),
            'experience_years': 18,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Mary Brown - (214) 555-1235',
            'notes': 'Retired maintenance supervisor, very reliable and experienced with home repairs'
        },
        # Illinois volunteers
        {
            'name': 'Nancy Taylor',
            'age': 44,
            'location': 'Chicago, IL',
            'phone': '(312) 555-1345',
            'email': 'nancy.taylor@email.com',
            'skills': json.dumps(['cooking', 'meal_planning', 'light_housekeeping', 'companionship']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '9:00-17:00',
                'tuesday': '9:00-17:00',
                'wednesday': '9:00-17:00',
                'thursday': '9:00-17:00',
                'friday': '9:00-17:00',
                'saturday': '10:00-14:00',
                'sunday': 'flexible'
            }),
            'experience_years': 11,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Robert Taylor - (312) 555-1346',
            'notes': 'Former restaurant manager, excellent at meal planning and nutrition for seniors'
        },
        {
            'name': 'Kevin Lee',
            'age': 27,
            'location': 'Springfield, IL',
            'phone': '(217) 555-1456',
            'email': 'kevin.lee@email.com',
            'skills': json.dumps(['technology_help', 'errands', 'companionship', 'reading']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '16:00-22:00',
                'tuesday': '16:00-22:00',
                'wednesday': '16:00-22:00',
                'thursday': '16:00-22:00',
                'friday': '16:00-22:00',
                'saturday': '10:00-18:00',
                'sunday': '10:00-18:00'
            }),
            'experience_years': 1,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Jennifer Lee - (217) 555-1457',
            'notes': 'Recent college graduate, very patient and tech-savvy, enjoys reading with seniors'
        },
        # Ohio volunteers
        {
            'name': 'Michelle White',
            'age': 39,
            'location': 'Columbus, OH',
            'phone': '(614) 555-1567',
            'email': 'michelle.white@email.com',
            'skills': json.dumps(['healthcare_support', 'medication_management', 'companionship', 'transportation']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '8:00-16:00',
                'tuesday': '8:00-16:00',
                'wednesday': '8:00-16:00',
                'thursday': '8:00-16:00',
                'friday': '8:00-16:00',
                'saturday': 'flexible',
                'sunday': 'flexible'
            }),
            'experience_years': 13,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Daniel White - (614) 555-1568',
            'notes': 'Licensed practical nurse with extensive experience in geriatric care'
        },
        {
            'name': 'Christopher Johnson',
            'age': 52,
            'location': 'Cleveland, OH',
            'phone': '(216) 555-1678',
            'email': 'christopher.johnson@email.com',
            'skills': json.dumps(['companionship', 'reading', 'crafts', 'pet_care']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '10:00-18:00',
                'tuesday': '10:00-18:00',
                'wednesday': '10:00-18:00',
                'thursday': '10:00-18:00',
                'friday': '10:00-18:00',
                'saturday': '9:00-15:00',
                'sunday': '9:00-15:00'
            }),
            'experience_years': 8,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Lisa Johnson - (216) 555-1679',
            'notes': 'Retired teacher, loves spending time with seniors and helping with hobbies'
        },
        # Pennsylvania volunteers
        {
            'name': 'Jessica Miller',
            'age': 31,
            'location': 'Philadelphia, PA',
            'phone': '(215) 555-1789',
            'email': 'jessica.miller@email.com',
            'skills': json.dumps(['cooking', 'grocery_shopping', 'companionship', 'light_housekeeping']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '11:00-19:00',
                'tuesday': '11:00-19:00',
                'wednesday': '11:00-19:00',
                'thursday': '11:00-19:00',
                'friday': '11:00-19:00',
                'saturday': '9:00-15:00',
                'sunday': 'flexible'
            }),
            'experience_years': 5,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Michael Miller - (215) 555-1790',
            'notes': 'Nutritionist with experience in senior dietary needs and meal preparation'
        },
        {
            'name': 'Daniel Wilson',
            'age': 46,
            'location': 'Pittsburgh, PA',
            'phone': '(412) 555-1890',
            'email': 'daniel.wilson@email.com',
            'skills': json.dumps(['transportation', 'errands', 'home_maintenance', 'companionship']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '8:00-16:00',
                'tuesday': '8:00-16:00',
                'wednesday': '8:00-16:00',
                'thursday': '8:00-16:00',
                'friday': '8:00-16:00',
                'saturday': '8:00-14:00',
                'sunday': 'unavailable'
            }),
            'experience_years': 10,
            'languages': json.dumps(['English']),
            'transportation': 'car',
            'background_check': True,
            'emergency_contact': 'Karen Wilson - (412) 555-1891',
            'notes': 'Former delivery driver, very reliable for transportation and running errands'
        },
        # Washington volunteers
        {
            'name': 'Rachel Green',
            'age': 36,
            'location': 'Seattle, WA',
            'phone': '(206) 555-1901',
            'email': 'rachel.green@email.com',
            'skills': json.dumps(['companionship', 'reading', 'technology_help', 'pet_care']),
            'availability_status': 'available',
            'availability_schedule': json.dumps({
                'monday': '12:00-20:00',
                'tuesday': '12:00-20:00',
                'wednesday': '12:00-20:00',
                'thursday': '12:00-20:00',
                'friday': '12:00-20:00',
                'saturday': '10:00-16:00',
                'sunday': '10:00-16:00'
            }),
            'experience_years': 7,
            'languages': json.dumps(['English']),
            'transportation': 'public_transport',
            'background_check': True,
            'emergency_contact': 'Ross Green - (206) 555-1902',
            'notes': 'Former librarian and dog trainer, great with both seniors and their pets'
        }
    ]
    
    # Insert sample data
    for volunteer in volunteers_data:
        cursor.execute('''
            INSERT INTO volunteers (
                name, age, location, phone, email, skills, availability_status,
                availability_schedule, experience_years, languages, transportation,
                background_check, emergency_contact, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            volunteer['name'], volunteer['age'], volunteer['location'],
            volunteer['phone'], volunteer['email'], volunteer['skills'],
            volunteer['availability_status'], volunteer['availability_schedule'],
            volunteer['experience_years'], volunteer['languages'],
            volunteer['transportation'], volunteer['background_check'],
            volunteer['emergency_contact'], volunteer['notes']
        ))
    
    pg_conn.commit()
    print(f"SUCCESS: Created {len(volunteers_data)} sample volunteer records in PostgreSQL!")
    return len(volunteers_data)

def check_existing_data(pg_conn):
    """Check if volunteers table already has data"""
    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM volunteers")
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except:
        return False

def verify_migration(pg_conn):
    """Verify the migration was successful"""
    cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
    
    # Count total records
    cursor.execute("SELECT COUNT(*) as count FROM volunteers")
    total_count = cursor.fetchone()['count']
    
    # Get sample records
    cursor.execute("SELECT name, location, skills, availability_status FROM volunteers LIMIT 3")
    sample_records = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print("MIGRATION VERIFICATION:")
    print(f"{'='*60}")
    print(f"Total records in PostgreSQL: {total_count}")
    print(f"\nSample records:")
    for record in sample_records:
        print(f"  - {record['name']} from {record['location']} ({record['availability_status']})")
    
    cursor.close()
    return total_count > 0

def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("Volunteers Database Migration")
    print("SQLite -> PostgreSQL (Coolify)")
    print("="*60 + "\n")
    
    # Step 1: Connect to PostgreSQL
    print("Step 1: Connecting to PostgreSQL Database...")
    pg_conn = get_postgres_connection()
    if pg_conn is None:
        print("\n✗ Migration failed: Could not connect to PostgreSQL database.")
        return False
    
    # Step 2: Connect to SQLite (optional)
    print("\nStep 2: Checking for SQLite database...")
    sqlite_conn = get_sqlite_connection()
    
    try:
        # Step 3: Create PostgreSQL table
        print("\nStep 3: Creating volunteers table in PostgreSQL...")
        create_postgres_table(pg_conn)
        
        # Step 4: Migrate data from SQLite if available
        print("\nStep 4: Migrating data...")
        migrated_count = migrate_data_from_sqlite(sqlite_conn, pg_conn)
        
        # Step 5: Create sample data if no SQLite data was migrated
        if migrated_count == 0:
            print("\nStep 5: Creating sample U.S. volunteers data...")
            create_sample_data(pg_conn)
        
        # Step 6: Verify migration
        print("\nStep 6: Verifying migration...")
        if verify_migration(pg_conn):
            print("\n" + "="*60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("\nYour volunteers database is now running on PostgreSQL!")
            print("\nNext steps:")
            print("1. Update your docker-compose.yaml (already done ✓)")
            print("2. Ensure tools.yaml is using 'postgres-sql' kind (already done ✓)")
            print("3. Deploy to Coolify or test locally")
            print("4. Consider backing up your SQLite database")
            return True
        else:
            print("\n✗ Migration verification failed.")
            return False
            
    except Exception as e:
        print(f"\n✗ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close connections
        if sqlite_conn:
            sqlite_conn.close()
        if pg_conn:
            pg_conn.close()
        print("\nDatabase connections closed.")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)