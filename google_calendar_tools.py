"""
Google Calendar Tools for LiveKit Voice Agent
Provides comprehensive calendar management functionality using Google Calendar API
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from livekit.agents import function_tool, RunContext

# Configure logging
logger = logging.getLogger("google_calendar_tools")
logger.setLevel(logging.DEBUG)

class GoogleCalendarManager:
    """Manages Google Calendar API interactions with OAuth authentication"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self.credentials_file = "gcp-oauth.keys.json"
        self.token_file = "google_calendar_token.json"
        
    def _create_credentials_file_from_env(self) -> bool:
        """Create credentials file from environment variables for Coolify deployment"""
        try:
            # Check if we have environment variables for OAuth credentials
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            project_id = os.getenv("GOOGLE_PROJECT_ID")
            
            if client_id and client_secret and project_id:
                # Create credentials file from environment variables
                credentials_data = {
                    "installed": {
                        "client_id": client_id,
                        "project_id": project_id,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": client_secret,
                        "redirect_uris": ["http://localhost:3500/oauth2callback"]
                    }
                }
                
                with open(self.credentials_file, 'w') as f:
                    json.dump(credentials_data, f)
                
                logger.info("✅ Created OAuth credentials file from environment variables")
                return True
            else:
                logger.info("ℹ️ No environment variables found for OAuth credentials, checking for file...")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create credentials file from environment: {e}")
            return False
        
    async def authenticate(self) -> bool:
        """Authenticate with Google Calendar API"""
        try:
            # First, try to create credentials file from environment variables (for Coolify)
            if not os.path.exists(self.credentials_file):
                if not self._create_credentials_file_from_env():
                    logger.error(f"❌ No OAuth credentials available (file or environment variables)")
                    return False
            
            # Load existing token if available
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, self.SCOPES
                )
            
            # If there are no valid credentials, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # Refresh expired credentials
                    self.credentials.refresh(Request())
                    logger.info("✅ Refreshed Google Calendar credentials")
                else:
                    # For containerized deployments, we need pre-authorized tokens
                    # Check if we have a refresh token in environment variables
                    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
                    
                    if refresh_token:
                        # Create credentials from refresh token
                        client_id = os.getenv("GOOGLE_CLIENT_ID")
                        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
                        
                        if client_id and client_secret:
                            self.credentials = Credentials(
                                token=None,
                                refresh_token=refresh_token,
                                token_uri="https://oauth2.googleapis.com/token",
                                client_id=client_id,
                                client_secret=client_secret,
                                scopes=self.SCOPES
                            )
                            
                            # Refresh to get access token
                            self.credentials.refresh(Request())
                            logger.info("✅ Created credentials from refresh token")
                        else:
                            logger.error("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET for refresh token")
                            return False
                    else:
                        logger.error("❌ No valid credentials or refresh token available")
                        logger.error("💡 For Coolify deployment, set GOOGLE_REFRESH_TOKEN environment variable")
                        logger.error("💡 Or complete OAuth flow locally first to generate tokens")
                        return False
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(self.credentials.to_json())
                    
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("✅ Google Calendar service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with Google Calendar: {e}")
            return False
    
    async def list_calendars(self) -> List[Dict[str, Any]]:
        """List all available calendars"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
                
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            logger.info(f"📅 Found {len(calendars)} calendars")
            return calendars
            
        except Exception as e:
            logger.error(f"❌ Failed to list calendars: {e}")
            raise
    
    async def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
                
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            logger.info(f"✅ Created event: {event.get('summary', 'Untitled')} at {event.get('start', {}).get('dateTime', 'No time')}")
            return event
            
        except Exception as e:
            logger.error(f"❌ Failed to create event: {e}")
            raise
    
    async def list_events(self, calendar_id: str = 'primary', max_results: int = 10, 
                         time_min: Optional[datetime] = None, time_max: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """List events from a calendar"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
            
            # Default to next 7 days if no time range specified
            if not time_min:
                time_min = datetime.utcnow()
            if not time_max:
                time_max = time_min + timedelta(days=7)
                
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"📋 Found {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to list events: {e}")
            raise
    
    async def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
                
            event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            logger.info(f"✅ Updated event: {event.get('summary', 'Untitled')}")
            return event
            
        except Exception as e:
            logger.error(f"❌ Failed to update event: {e}")
            raise
    
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete an event"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
                
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"✅ Deleted event: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete event: {e}")
            raise
    
    async def search_events(self, calendar_id: str, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for events by text query"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
                
            events_result = self.service.events().list(
                calendarId=calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"🔍 Found {len(events)} events matching '{query}'")
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to search events: {e}")
            raise
    
    async def get_freebusy(self, calendar_ids: List[str], time_min: datetime, time_max: datetime) -> Dict[str, Any]:
        """Check free/busy status for calendars"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")
                
            body = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'items': [{'id': cal_id} for cal_id in calendar_ids]
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            logger.info(f"📊 Retrieved free/busy data for {len(calendar_ids)} calendars")
            return freebusy_result
            
        except Exception as e:
            logger.error(f"❌ Failed to get free/busy data: {e}")
            raise

# Global calendar manager instance
calendar_manager = GoogleCalendarManager()

# LiveKit Function Tools

@function_tool()
async def list_calendars(context: RunContext) -> str:
    """List all available Google calendars.
    
    Returns:
        A formatted string listing all available calendars with their names and IDs.
    """
    try:
        calendars = await calendar_manager.list_calendars()
        
        if not calendars:
            return "No calendars found. Please make sure you have access to Google Calendar."
        
        result = "📅 **Available Calendars:**\n\n"
        for calendar in calendars:
            name = calendar.get('summary', 'Unnamed Calendar')
            cal_id = calendar.get('id', 'No ID')
            primary = " (Primary)" if calendar.get('primary', False) else ""
            result += f"• **{name}**{primary}\n  ID: {cal_id}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error listing calendars: {e}")
        return f"❌ Sorry, I couldn't retrieve your calendars. Error: {str(e)}"

@function_tool()
async def create_event(
    context: RunContext,
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    location: str = "",
    calendar_id: str = "primary"
) -> str:
    """Create a new calendar event.
    
    Args:
        title: The title/summary of the event
        start_datetime: Start date and time in ISO format (e.g., "2024-01-15T10:00:00")
        end_datetime: End date and time in ISO format (e.g., "2024-01-15T11:00:00")
        description: Optional description of the event
        location: Optional location of the event
        calendar_id: Calendar ID to create the event in (default: "primary")
    
    Returns:
        A confirmation message with event details.
    """
    try:
        # Parse datetime strings
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
        except ValueError as e:
            return f"❌ Invalid date format. Please use ISO format like '2024-01-15T10:00:00'. Error: {str(e)}"
        
        event_data = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        event = await calendar_manager.create_event(calendar_id, event_data)
        
        return f"✅ **Event Created Successfully!**\n\n" \
               f"📅 **{title}**\n" \
               f"🕐 **Start:** {start_datetime}\n" \
               f"🕑 **End:** {end_datetime}\n" \
               f"📍 **Location:** {location or 'Not specified'}\n" \
               f"📝 **Description:** {description or 'No description'}\n" \
               f"🆔 **Event ID:** {event.get('id', 'Unknown')}"
        
    except Exception as e:
        logger.error(f"❌ Error creating event: {e}")
        return f"❌ Sorry, I couldn't create the event. Error: {str(e)}"

@function_tool()
async def list_events(
    context: RunContext,
    calendar_id: str = "primary",
    days_ahead: int = 7,
    max_results: int = 10
) -> str:
    """List upcoming events from a calendar.
    
    Args:
        calendar_id: Calendar ID to list events from (default: "primary")
        days_ahead: Number of days ahead to look for events (default: 7)
        max_results: Maximum number of events to return (default: 10)
    
    Returns:
        A formatted string listing upcoming events.
    """
    try:
        time_min = datetime.utcnow()
        time_max = time_min + timedelta(days=days_ahead)
        
        events = await calendar_manager.list_events(calendar_id, max_results, time_min, time_max)
        
        if not events:
            return f"📅 No upcoming events found in the next {days_ahead} days."
        
        result = f"📅 **Upcoming Events (Next {days_ahead} days):**\n\n"
        
        for event in events:
            title = event.get('summary', 'Untitled Event')
            start = event.get('start', {})
            start_time = start.get('dateTime', start.get('date', 'No time specified'))
            location = event.get('location', 'No location')
            description = event.get('description', 'No description')
            
            # Format datetime for display
            try:
                if 'T' in start_time:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
                else:
                    formatted_time = start_time
            except:
                formatted_time = start_time
            
            result += f"• **{title}**\n"
            result += f"  🕐 {formatted_time}\n"
            result += f"  📍 {location}\n"
            if description and description != 'No description':
                result += f"  📝 {description[:100]}{'...' if len(description) > 100 else ''}\n"
            result += f"  🆔 ID: {event.get('id', 'Unknown')}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error listing events: {e}")
        return f"❌ Sorry, I couldn't retrieve your events. Error: {str(e)}"

@function_tool()
async def search_events(
    context: RunContext,
    query: str,
    calendar_id: str = "primary",
    max_results: int = 10
) -> str:
    """Search for events by text query.
    
    Args:
        query: Text to search for in event titles, descriptions, and locations
        calendar_id: Calendar ID to search in (default: "primary")
        max_results: Maximum number of events to return (default: 10)
    
    Returns:
        A formatted string listing matching events.
    """
    try:
        events = await calendar_manager.search_events(calendar_id, query, max_results)
        
        if not events:
            return f"🔍 No events found matching '{query}'."
        
        result = f"🔍 **Events matching '{query}':**\n\n"
        
        for event in events:
            title = event.get('summary', 'Untitled Event')
            start = event.get('start', {})
            start_time = start.get('dateTime', start.get('date', 'No time specified'))
            location = event.get('location', 'No location')
            
            # Format datetime for display
            try:
                if 'T' in start_time:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
                else:
                    formatted_time = start_time
            except:
                formatted_time = start_time
            
            result += f"• **{title}**\n"
            result += f"  🕐 {formatted_time}\n"
            result += f"  📍 {location}\n"
            result += f"  🆔 ID: {event.get('id', 'Unknown')}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error searching events: {e}")
        return f"❌ Sorry, I couldn't search your events. Error: {str(e)}"

@function_tool()
async def update_event(
    context: RunContext,
    event_id: str,
    calendar_id: str = "primary",
    title: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """Update an existing calendar event.
    
    Args:
        event_id: The ID of the event to update
        calendar_id: Calendar ID containing the event (default: "primary")
        title: New title for the event (optional)
        start_datetime: New start date/time in ISO format (optional)
        end_datetime: New end date/time in ISO format (optional)
        description: New description (optional)
        location: New location (optional)
    
    Returns:
        A confirmation message with updated event details.
    """
    try:
        # First, get the existing event
        if not await calendar_manager.authenticate():
            raise Exception("Authentication failed")
            
        existing_event = calendar_manager.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        # Update only the provided fields
        event_data = existing_event.copy()
        
        if title:
            event_data['summary'] = title
        if description is not None:
            event_data['description'] = description
        if location is not None:
            event_data['location'] = location
        
        if start_datetime:
            try:
                start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                event_data['start'] = {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC',
                }
            except ValueError as e:
                return f"❌ Invalid start date format. Please use ISO format like '2024-01-15T10:00:00'. Error: {str(e)}"
        
        if end_datetime:
            try:
                end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                event_data['end'] = {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                }
            except ValueError as e:
                return f"❌ Invalid end date format. Please use ISO format like '2024-01-15T10:00:00'. Error: {str(e)}"
        
        updated_event = await calendar_manager.update_event(calendar_id, event_id, event_data)
        
        return f"✅ **Event Updated Successfully!**\n\n" \
               f"📅 **{updated_event.get('summary', 'Untitled')}**\n" \
               f"🆔 **Event ID:** {event_id}\n" \
               f"📝 **Updated fields:** {', '.join([f for f in ['title', 'start_datetime', 'end_datetime', 'description', 'location'] if locals().get(f) is not None])}"
        
    except Exception as e:
        logger.error(f"❌ Error updating event: {e}")
        return f"❌ Sorry, I couldn't update the event. Error: {str(e)}"

@function_tool()
async def delete_event(
    context: RunContext,
    event_id: str,
    calendar_id: str = "primary"
) -> str:
    """Delete a calendar event.
    
    Args:
        event_id: The ID of the event to delete
        calendar_id: Calendar ID containing the event (default: "primary")
    
    Returns:
        A confirmation message.
    """
    try:
        success = await calendar_manager.delete_event(calendar_id, event_id)
        
        if success:
            return f"✅ **Event Deleted Successfully!**\n\n🆔 **Event ID:** {event_id}"
        else:
            return f"❌ Failed to delete event with ID: {event_id}"
        
    except Exception as e:
        logger.error(f"❌ Error deleting event: {e}")
        return f"❌ Sorry, I couldn't delete the event. Error: {str(e)}"

@function_tool()
async def get_freebusy(
    context: RunContext,
    start_datetime: str,
    end_datetime: str,
    calendar_ids: Optional[List[str]] = None
) -> str:
    """Check free/busy status for calendars in a time range.
    
    Args:
        start_datetime: Start of time range in ISO format (e.g., "2024-01-15T09:00:00")
        end_datetime: End of time range in ISO format (e.g., "2024-01-15T17:00:00")
        calendar_ids: List of calendar IDs to check (default: ["primary"])
    
    Returns:
        A formatted string showing busy periods.
    """
    try:
        if not calendar_ids:
            calendar_ids = ["primary"]
        
        # Parse datetime strings
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
        except ValueError as e:
            return f"❌ Invalid date format. Please use ISO format like '2024-01-15T10:00:00'. Error: {str(e)}"
        
        freebusy_data = await calendar_manager.get_freebusy(calendar_ids, start_dt, end_dt)
        
        result = f"📊 **Free/Busy Status**\n"
        result += f"🕐 **Time Range:** {start_datetime} to {end_datetime}\n\n"
        
        calendars = freebusy_data.get('calendars', {})
        
        for cal_id in calendar_ids:
            cal_data = calendars.get(cal_id, {})
            busy_periods = cal_data.get('busy', [])
            
            result += f"📅 **Calendar:** {cal_id}\n"
            
            if not busy_periods:
                result += "✅ **Status:** Completely free during this time\n\n"
            else:
                result += f"⏰ **Busy Periods:** {len(busy_periods)} conflicts found\n"
                for period in busy_periods:
                    start_busy = period.get('start', 'Unknown')
                    end_busy = period.get('end', 'Unknown')
                    
                    # Format times for display
                    try:
                        start_formatted = datetime.fromisoformat(start_busy.replace('Z', '+00:00')).strftime('%I:%M %p')
                        end_formatted = datetime.fromisoformat(end_busy.replace('Z', '+00:00')).strftime('%I:%M %p')
                        result += f"  • {start_formatted} - {end_formatted}\n"
                    except:
                        result += f"  • {start_busy} - {end_busy}\n"
                result += "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting free/busy data: {e}")
        return f"❌ Sorry, I couldn't check the free/busy status. Error: {str(e)}"

# Helper function to format datetime for user-friendly display
def format_datetime_for_display(iso_string: str) -> str:
    """Convert ISO datetime string to user-friendly format"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        return iso_string