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
    
    # Sample volunteer data from various US states (20 records)
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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
            'background_check': 1,
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