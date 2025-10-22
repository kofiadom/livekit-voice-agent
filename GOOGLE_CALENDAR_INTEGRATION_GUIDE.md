# Google Calendar Integration Guide

This guide explains how to set up and use the custom Google Calendar integration in your LiveKit Voice Agent.

## Overview

We've replaced the Google Calendar MCP server with custom LiveKit function tools that provide direct Google Calendar API integration. This approach is more reliable and easier to manage than the MCP server.

## Features

The integration provides the following calendar management capabilities:

### Available Tools

1. **`list_calendars`** - List all available Google calendars
2. **`create_event`** - Create new calendar events
3. **`list_events`** - List upcoming events from a calendar
4. **`search_events`** - Search for events by text query
5. **`update_event`** - Update existing events
6. **`delete_event`** - Delete calendar events
7. **`get_freebusy`** - Check availability across calendars

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
4. Create OAuth 2.0 credentials:
   - Go to **Credentials** → **Create Credentials** → **OAuth client ID**
   - Choose **Desktop application** as the application type
   - Download the credentials file
   - Rename it to `gcp-oauth.keys.json` and place it in your project root

### 2. OAuth Consent Screen

1. Go to **OAuth consent screen** in Google Cloud Console
2. Configure your app information
3. Add your email as a test user
4. Add the following scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`

### 3. Project Setup

The integration is already configured in your project:

- ✅ **Dependencies added** to `requirements.txt`
- ✅ **Custom tools created** in `google_calendar_tools.py`
- ✅ **Agent updated** to include calendar tools
- ✅ **MCP server removed** from docker-compose.yaml

## Authentication Flow

### First-Time Setup

1. When the agent first tries to use calendar tools, it will check for existing authentication
2. If no valid token exists, you'll need to complete the OAuth flow:
   - The system will log an authorization URL
   - Visit the URL in your browser
   - Grant permissions to your application
   - You'll be redirected to `http://localhost:3500/oauth2callback`
   - The authorization code will be in the URL

### Token Management

- Tokens are automatically saved to `google_calendar_token.json`
- Expired tokens are automatically refreshed
- The system handles authentication transparently after initial setup


## Required Environment Variables

You need to set these environment variables in your Coolify deployment:

### 1. OAuth Client Credentials

From your `gcp-oauth.keys.json` file, extract these values:

```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here  
GOOGLE_PROJECT_ID=your_project_id_here
```

### 2. Refresh Token (Most Important)

```bash
GOOGLE_REFRESH_TOKEN=your_refresh_token_here
```

## How to Get the Refresh Token

### Method 1: Local OAuth Flow (Recommended)

1. **Run the agent locally first** with your `gcp-oauth.keys.json` file
2. **Complete the OAuth flow** when prompted
3. **Check the generated token file** `google_calendar_token.json`
4. **Extract the refresh_token** from the JSON file

Example `google_calendar_token.json`:
```json
{
  "token": "ya29.a0...",
  "refresh_token": "1//04...",  ← This is what you need
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "scopes": ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]
}
```

### Method 2: Manual OAuth Flow

If you can't run locally, you can get the refresh token manually:

1. **Create OAuth URL:**
```
https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3500/oauth2callback&scope=https://www.googleapis.com/auth/calendar%20https://www.googleapis.com/auth/calendar.events&response_type=code&access_type=offline&prompt=consent
```

2. **Visit the URL** and authorize your application
3. **Get the authorization code** from the redirect URL
4. **Exchange for tokens** using curl:

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=AUTHORIZATION_CODE" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=http://localhost:3500/oauth2callback"
```

5. **Extract refresh_token** from the response

## Deployment Process

### 1. Set Environment Variables

Configure all the Google Calendar environment variables in Coolify as shown above.

### 2. Deploy Your Application

The application will automatically:
- Create OAuth credentials file from environment variables
- Use the refresh token to get access tokens
- Handle token refresh automatically
- Provide full calendar functionality

### 3. Verify Integration

Check the application logs for:
```
✅ Created OAuth credentials file from environment variables
✅ Created credentials from refresh token
✅ Google Calendar service initialized successfully
📅 Custom Google Calendar tools: 7 tools found
```

## Usage Examples

### Voice Commands

Users can now say things like:

**Calendar Management:**
- "Show me my calendars"
- "List my upcoming events"
- "What do I have scheduled for tomorrow?"
- "Search for doctor appointments"

**Event Creation:**
- "Schedule a meeting with Sarah Johnson for cooking help tomorrow at 2 PM"
- "Create an appointment for transportation to the hospital on Friday at 10 AM"
- "Book a companionship visit with Mary next Tuesday at 3 PM"

**Event Management:**
- "Update my appointment with John to 4 PM instead"
- "Cancel my meeting on Thursday"
- "Check if I'm free tomorrow afternoon"

### Integration with Volunteer System

The calendar tools work seamlessly with the volunteer management system:

1. **Find Volunteers** → Use MCP toolbox to search volunteer database
2. **Schedule Appointments** → Use calendar tools to create events
3. **Manage Appointments** → Update, cancel, or search for volunteer appointments


## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check that `gcp-oauth.keys.json` exists and is valid
   - Ensure you've completed the OAuth consent screen setup
   - Verify your email is added as a test user

2. **"Invalid date format"**
   - Use ISO format: `2024-01-15T10:00:00`
   - The system expects UTC times

3. **"Calendar not found"**
   - Use `list_calendars` to see available calendar IDs
   - Default calendar ID is "primary"

### Debug Logging

The system provides comprehensive logging:
- Authentication status
- API calls and responses
- Error details with suggestions

## Security

- OAuth credentials are stored locally
- Tokens are automatically refreshed
- All API calls use secure HTTPS
- Credentials never leave your deployment environment

