from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Volunteer API",
    description="REST API for accessing volunteer data from Postgres database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class VolunteerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=18, le=100)
    location: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    skills: str = Field(..., description="Comma-separated skills or JSON array")
    available: bool = Field(default=True)
    years_experience: int = Field(default=0, ge=0)
    languages: Optional[str] = Field(None, description="Comma-separated languages or JSON array")
    transportation: Optional[str] = Field(None, pattern="^(car|public_transport|walking|bicycle)$")
    background_check: bool = Field(default=False)
    emergency_contact: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

class VolunteerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    age: Optional[int] = Field(None, ge=18, le=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    skills: Optional[str] = None
    available: Optional[bool] = None
    years_experience: Optional[int] = Field(None, ge=0)
    languages: Optional[str] = None
    transportation: Optional[str] = Field(None, pattern="^(car|public_transport|walking|bicycle)$")
    background_check: Optional[bool] = None
    emergency_contact: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

def get_db_connection():
    """Connect to Postgres using the same env vars as other services"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Volunteer API is running",
        "version": "1.0.0",
        "endpoints": {
            "volunteers": "/api/volunteers",
            "volunteer_by_id": "/api/volunteers/{id}",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@app.get("/openapi-test")
async def openapi_test():
    """Test endpoint to check if OpenAPI schema generation works"""
    try:
        from fastapi.openapi.utils import get_openapi
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        return {"status": "success", "schema_keys": list(schema.keys())}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "service": "volunteer-api"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/volunteers")
async def get_volunteers(
    skill: Optional[str] = None,
    location: Optional[str] = None,
    available: Optional[bool] = None,
    language: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Get all volunteers with optional filters
    
    Query Parameters:
    - skill: Filter by skill (partial match)
    - location: Filter by location (partial match)
    - available: Filter by availability (true/false)
    - language: Filter by language (partial match)
    - limit: Maximum number of results (default: 100)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM volunteers WHERE 1=1"
        params = []
        
        if skill:
            query += " AND skills ILIKE %s"
            params.append(f"%{skill}%")
        
        if location:
            query += " AND location ILIKE %s"
            params.append(f"%{location}%")
        
        if available is not None:
            query += " AND available = %s"
            params.append(available)
        
        if language:
            query += " AND languages ILIKE %s"
            params.append(f"%{language}%")
        
        query += f" LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        volunteers = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "volunteers": volunteers,
            "count": len(volunteers),
            "filters_applied": {
                "skill": skill,
                "location": location,
                "available": available,
                "language": language
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching volunteers: {str(e)}")

@app.get("/api/volunteers/{volunteer_id}")
async def get_volunteer(volunteer_id: int):
    """
    Get a specific volunteer by ID
    
    Path Parameters:
    - volunteer_id: The ID of the volunteer to retrieve
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM volunteers WHERE id = %s", (volunteer_id,))
        volunteer = cur.fetchone()
        cur.close()
        conn.close()
        
        if not volunteer:
            raise HTTPException(
                status_code=404,
                detail=f"Volunteer with ID {volunteer_id} not found"
            )
        
        return volunteer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching volunteer: {str(e)}")

@app.get("/api/volunteers/search/by-skill/{skill}")
async def search_by_skill(skill: str, limit: int = 50):
    """
    Search volunteers by specific skill
    
    Path Parameters:
    - skill: The skill to search for
    
    Query Parameters:
    - limit: Maximum number of results (default: 50)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM volunteers WHERE skills ILIKE %s LIMIT %s",
            (f"%{skill}%", limit)
        )
        volunteers = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "skill_searched": skill,
            "volunteers": volunteers,
            "count": len(volunteers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching by skill: {str(e)}")

@app.get("/api/volunteers/search/by-location/{location}")
async def search_by_location(location: str, limit: int = 50):
    """
    Search volunteers by location
    
    Path Parameters:
    - location: The location to search for
    
    Query Parameters:
    - limit: Maximum number of results (default: 50)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM volunteers WHERE location ILIKE %s LIMIT %s",
            (f"%{location}%", limit)
        )
        volunteers = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "location_searched": location,
            "volunteers": volunteers,
            "count": len(volunteers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching by location: {str(e)}")

@app.get("/api/volunteers/available")
async def get_available_volunteers(limit: int = 50):
    """
    Get all currently available volunteers
    
    Query Parameters:
    - limit: Maximum number of results (default: 50)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM volunteers WHERE available = true LIMIT %s",
            (limit,)
        )
        volunteers = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "volunteers": volunteers,
            "count": len(volunteers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available volunteers: {str(e)}")

@app.post("/api/volunteers", status_code=status.HTTP_201_CREATED)
async def create_volunteer(volunteer: VolunteerCreate):
    """
    Create a new volunteer
    
    Request Body:
    - name: Volunteer's full name (required)
    - age: Age between 18-100 (required)
    - location: City and state (required)
    - phone: Contact phone number (optional)
    - email: Email address (optional)
    - skills: Skills as comma-separated string or JSON array (required)
    - available: Availability status (default: true)
    - years_experience: Years of experience (default: 0)
    - languages: Languages spoken (optional)
    - transportation: Transportation method (car, public_transport, walking, bicycle)
    - background_check: Background check status (default: false)
    - emergency_contact: Emergency contact info (optional)
    - notes: Additional notes (optional)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO volunteers (
                name, age, location, phone, email, skills, available,
                years_experience, languages, transportation, background_check,
                emergency_contact, notes, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING *
        """, (
            volunteer.name,
            volunteer.age,
            volunteer.location,
            volunteer.phone,
            volunteer.email,
            volunteer.skills,
            volunteer.available,
            volunteer.years_experience,
            volunteer.languages,
            volunteer.transportation,
            volunteer.background_check,
            volunteer.emergency_contact,
            volunteer.notes
        ))
        
        new_volunteer = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "Volunteer created successfully",
            "volunteer": new_volunteer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating volunteer: {str(e)}")

@app.put("/api/volunteers/{volunteer_id}")
async def update_volunteer(volunteer_id: int, volunteer: VolunteerUpdate):
    """
    Update an existing volunteer
    
    Path Parameters:
    - volunteer_id: The ID of the volunteer to update
    
    Request Body: (all fields optional)
    - name: Volunteer's full name
    - age: Age between 18-100
    - location: City and state
    - phone: Contact phone number
    - email: Email address
    - skills: Skills as comma-separated string or JSON array
    - available: Availability status
    - years_experience: Years of experience
    - languages: Languages spoken
    - transportation: Transportation method
    - background_check: Background check status
    - emergency_contact: Emergency contact info
    - notes: Additional notes
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if volunteer exists
        cur.execute("SELECT id FROM volunteers WHERE id = %s", (volunteer_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Volunteer with ID {volunteer_id} not found")
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        for field, value in volunteer.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)
        
        if not update_fields:
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Add updated_at timestamp
        update_fields.append("updated_at = NOW()")
        update_values.append(volunteer_id)
        
        query = f"""
            UPDATE volunteers
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """
        
        cur.execute(query, update_values)
        updated_volunteer = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "Volunteer updated successfully",
            "volunteer": updated_volunteer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating volunteer: {str(e)}")

@app.delete("/api/volunteers/{volunteer_id}", status_code=status.HTTP_200_OK)
async def delete_volunteer(volunteer_id: int):
    """
    Delete a volunteer
    
    Path Parameters:
    - volunteer_id: The ID of the volunteer to delete
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if volunteer exists and get their info before deleting
        cur.execute("SELECT * FROM volunteers WHERE id = %s", (volunteer_id,))
        volunteer = cur.fetchone()
        
        if not volunteer:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Volunteer with ID {volunteer_id} not found")
        
        # Delete the volunteer
        cur.execute("DELETE FROM volunteers WHERE id = %s", (volunteer_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "Volunteer deleted successfully",
            "deleted_volunteer": volunteer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting volunteer: {str(e)}")

@app.patch("/api/volunteers/{volunteer_id}/availability")
async def update_volunteer_availability(volunteer_id: int, available: bool):
    """
    Quick update for volunteer availability status
    
    Path Parameters:
    - volunteer_id: The ID of the volunteer
    
    Query Parameters:
    - available: New availability status (true/false)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            UPDATE volunteers
            SET available = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING *
        """, (available, volunteer_id))
        
        updated_volunteer = cur.fetchone()
        
        if not updated_volunteer:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Volunteer with ID {volunteer_id} not found")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "Availability updated successfully",
            "volunteer": updated_volunteer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating availability: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)