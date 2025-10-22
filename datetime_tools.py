"""
DateTime Tools for LiveKit Voice Agent
Provides current date and time information for elderly users
"""

import logging
from datetime import datetime
from typing import Optional
import pytz

from livekit.agents import function_tool, RunContext

# Configure logging
logger = logging.getLogger("datetime_tools")
logger.setLevel(logging.DEBUG)

@function_tool()
async def get_current_datetime(context: RunContext, timezone: str = "US/Eastern") -> str:
    """Get the current date and time in a user-friendly format.
    
    Args:
        timezone: The timezone to display the time in (default: US/Eastern)
                 Common US timezones: US/Eastern, US/Central, US/Mountain, US/Pacific
    
    Returns:
        A formatted string with the current date and time.
    """
    try:
        # Get current time in the specified timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Format for elderly users - clear and easy to read
        formatted_date = current_time.strftime("%A, %B %d, %Y")
        formatted_time = current_time.strftime("%I:%M %p")
        
        result = f"📅 **Today is {formatted_date}**\n"
        result += f"🕐 **Current time: {formatted_time}**\n"
        result += f"🌍 **Timezone: {timezone}**"
        
        logger.info(f"✅ Provided current datetime: {formatted_date} at {formatted_time}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting current datetime: {e}")
        # Fallback to system time if timezone fails
        current_time = datetime.now()
        formatted_date = current_time.strftime("%A, %B %d, %Y")
        formatted_time = current_time.strftime("%I:%M %p")
        
        result = f"📅 **Today is {formatted_date}**\n"
        result += f"🕐 **Current time: {formatted_time}**\n"
        result += f"⚠️ **Note: Showing local system time**"
        
        return result

@function_tool()
async def get_current_date(context: RunContext, timezone: str = "US/Eastern") -> str:
    """Get just the current date in a user-friendly format.
    
    Args:
        timezone: The timezone to get the date for (default: US/Eastern)
    
    Returns:
        A formatted string with the current date.
    """
    try:
        # Get current date in the specified timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Format for elderly users
        formatted_date = current_time.strftime("%A, %B %d, %Y")
        day_of_week = current_time.strftime("%A")
        
        result = f"📅 **Today is {formatted_date}**\n"
        result += f"📆 **It's a {day_of_week}**"
        
        logger.info(f"✅ Provided current date: {formatted_date}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting current date: {e}")
        # Fallback to system time
        current_time = datetime.now()
        formatted_date = current_time.strftime("%A, %B %d, %Y")
        day_of_week = current_time.strftime("%A")
        
        result = f"📅 **Today is {formatted_date}**\n"
        result += f"📆 **It's a {day_of_week}**"
        
        return result

@function_tool()
async def get_current_time(context: RunContext, timezone: str = "US/Eastern") -> str:
    """Get just the current time in a user-friendly format.
    
    Args:
        timezone: The timezone to get the time for (default: US/Eastern)
    
    Returns:
        A formatted string with the current time.
    """
    try:
        # Get current time in the specified timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Format for elderly users
        formatted_time = current_time.strftime("%I:%M %p")
        
        result = f"🕐 **Current time: {formatted_time}**\n"
        result += f"🌍 **Timezone: {timezone}**"
        
        logger.info(f"✅ Provided current time: {formatted_time}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting current time: {e}")
        # Fallback to system time
        current_time = datetime.now()
        formatted_time = current_time.strftime("%I:%M %p")
        
        result = f"🕐 **Current time: {formatted_time}**\n"
        result += f"⚠️ **Note: Showing local system time**"
        
        return result

@function_tool()
async def get_day_of_week(context: RunContext, timezone: str = "US/Eastern") -> str:
    """Get the current day of the week.
    
    Args:
        timezone: The timezone to get the day for (default: US/Eastern)
    
    Returns:
        A formatted string with the current day of the week.
    """
    try:
        # Get current day in the specified timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        day_of_week = current_time.strftime("%A")
        
        result = f"📆 **Today is {day_of_week}**"
        
        logger.info(f"✅ Provided day of week: {day_of_week}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting day of week: {e}")
        # Fallback to system time
        current_time = datetime.now()
        day_of_week = current_time.strftime("%A")
        
        result = f"📆 **Today is {day_of_week}**"
        
        return result

# Helper function to format datetime for scheduling
def format_datetime_for_scheduling(dt: datetime) -> str:
    """Format datetime in a way that's suitable for calendar scheduling"""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

# Helper function to parse user-friendly date input
def parse_user_date_input(date_string: str) -> Optional[datetime]:
    """Parse common date formats that elderly users might use"""
    common_formats = [
        "%B %d, %Y",      # January 15, 2024
        "%B %d",          # January 15 (current year)
        "%m/%d/%Y",       # 01/15/2024
        "%m/%d",          # 01/15 (current year)
        "%Y-%m-%d",       # 2024-01-15
    ]
    
    for fmt in common_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            # If no year specified, use current year
            if parsed_date.year == 1900:
                parsed_date = parsed_date.replace(year=datetime.now().year)
            return parsed_date
        except ValueError:
            continue
    
    return None