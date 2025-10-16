import sqlite3
from datetime import datetime, date
import json

def create_volunteers_database():
    """Create SQLite database with volunteers table and sample data"""
    
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect('volunteers.db')
    cursor = conn.cursor()
    
    # Create volunteers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            location TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            skills TEXT NOT NULL,  -- JSON array of skills
            availability_status TEXT NOT NULL CHECK (availability_status IN ('available', 'busy', 'unavailable')),
            availability_schedule TEXT,  -- JSON object with schedule
            experience_years INTEGER DEFAULT 0,
            languages TEXT,  -- JSON array of languages spoken
            transportation TEXT CHECK (transportation IN ('car', 'public_transport', 'walking', 'bicycle')),
            background_check BOOLEAN DEFAULT 0,
            emergency_contact TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sample volunteer data
    volunteers_data = [
        {
            'name': 'Sarah Johnson',
            'age': 45,
            'location': 'Downtown, Accra',
            'phone': '+233-24-123-4567',
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
            'languages': json.dumps(['English', 'Twi']),
            'transportation': 'car',
            'background_check': 1,
            'emergency_contact': 'John Johnson - +233-24-765-4321',
            'notes': 'Specializes in elderly care, former nurse assistant'
        },
        {
            'name': 'Michael Asante',
            'age': 32,
            'location': 'East Legon, Accra',
            'phone': '+233-20-987-6543',
            'email': 'michael.asante@email.com',
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
            'languages': json.dumps(['English', 'Twi', 'Ga']),
            'transportation': 'car',
            'background_check': 1,
            'emergency_contact': 'Grace Asante - +233-24-111-2222',
            'notes': 'Tech-savvy, great with helping seniors use smartphones and computers'
        },
        {
            'name': 'Akosua Mensah',
            'age': 28,
            'location': 'Tema, Greater Accra',
            'phone': '+233-26-555-7890',
            'email': 'akosua.mensah@email.com',
            'skills': json.dumps(['physical_therapy_support', 'exercise_assistance', 'companionship', 'reading']),
            'availability_status': 'busy',
            'availability_schedule': json.dumps({
                'monday': 'unavailable',
                'tuesday': '16:00-19:00',
                'wednesday': 'unavailable',
                'thursday': '16:00-19:00',
                'friday': 'unavailable',
                'saturday': '9:00-15:00',
                'sunday': '9:00-15:00'
            }),
            'experience_years': 5,
            'languages': json.dumps(['English', 'Twi']),
            'transportation': 'public_transport',
            'background_check': 1,
            'emergency_contact': 'Kwame Mensah - +233-24-333-4444',
            'notes': 'Physical therapy background, excellent for mobility assistance'
        },
        {
            'name': 'Emmanuel Osei',
            'age': 55,
            'location': 'Kumasi, Ashanti Region',
            'phone': '+233-24-777-8888',
            'email': 'emmanuel.osei@email.com',
            'skills': json.dumps(['gardening', 'home_maintenance', 'companionship', 'storytelling']),
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
            'languages': json.dumps(['English', 'Twi', 'Asante Twi']),
            'transportation': 'bicycle',
            'background_check': 1,
            'emergency_contact': 'Mary Osei - +233-20-999-0000',
            'notes': 'Retired teacher, loves sharing stories and helping with garden work'
        },
        {
            'name': 'Fatima Abdul-Rahman',
            'age': 38,
            'location': 'Tamale, Northern Region',
            'phone': '+233-27-222-3333',
            'email': 'fatima.abdul@email.com',
            'skills': json.dumps(['cooking', 'cultural_activities', 'companionship', 'medication_reminders']),
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
            'languages': json.dumps(['English', 'Hausa', 'Dagbani']),
            'transportation': 'public_transport',
            'background_check': 1,
            'emergency_contact': 'Ibrahim Abdul-Rahman - +233-24-444-5555',
            'notes': 'Excellent cook, specializes in traditional Northern Ghanaian cuisine'
        },
        {
            'name': 'Joyce Appiah',
            'age': 42,
            'location': 'Cape Coast, Central Region',
            'phone': '+233-24-666-7777',
            'email': 'joyce.appiah@email.com',
            'skills': json.dumps(['healthcare_support', 'medication_management', 'companionship', 'light_housekeeping']),
            'availability_status': 'unavailable',
            'availability_schedule': json.dumps({
                'monday': 'unavailable',
                'tuesday': 'unavailable',
                'wednesday': 'unavailable',
                'thursday': 'unavailable',
                'friday': 'unavailable',
                'saturday': 'unavailable',
                'sunday': 'unavailable'
            }),
            'experience_years': 15,
            'languages': json.dumps(['English', 'Fante']),
            'transportation': 'car',
            'background_check': 1,
            'emergency_contact': 'Samuel Appiah - +233-20-888-9999',
            'notes': 'Registered nurse, currently on leave but will be available next month'
        }
    ]
    
    # Insert sample data
    for volunteer in volunteers_data:
        cursor.execute('''
            INSERT INTO volunteers (
                name, age, location, phone, email, skills, availability_status,
                availability_schedule, experience_years, languages, transportation,
                background_check, emergency_contact, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            volunteer['name'], volunteer['age'], volunteer['location'],
            volunteer['phone'], volunteer['email'], volunteer['skills'],
            volunteer['availability_status'], volunteer['availability_schedule'],
            volunteer['experience_years'], volunteer['languages'],
            volunteer['transportation'], volunteer['background_check'],
            volunteer['emergency_contact'], volunteer['notes']
        ))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("SUCCESS: Volunteers database created successfully!")
    print(f"INFO: Inserted {len(volunteers_data)} volunteer records")
    print("INFO: Database file: volunteers.db")

if __name__ == "__main__":
    create_volunteers_database()