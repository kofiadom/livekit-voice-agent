from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional

app = FastAPI(
    title="Volunteer API",
    description="REST API for accessing volunteer data from Postgres database",
    version="1.0.0"
)

# Enable CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "health": "/health"
        }
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)