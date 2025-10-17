# Google Calendar Integration Setup Guide

This guide will help you set up Google Calendar integration for the volunteer management system, allowing elderly users to schedule appointments with volunteers through the voice agent.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- The volunteer management system already deployed

## Step 1: Google Cloud Project Setup

### 1.1 Create or Select a Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Make sure the correct project is selected from the top bar

### 1.2 Enable Google Calendar API
1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click on "Google Calendar API" and click **Enable**
4. Wait for the API to be enabled (may take a few minutes)

## Step 2: Create OAuth 2.0 Credentials

### 2.1 Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace account)
3. Fill in the required information:
   - **App name**: "Volunteer Management System"
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Add the following scopes (optional but recommended):
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/calendar`
5. Add your email address as a **test user** under the Audience screen
6. Click **Save and Continue** through all steps

### 2.2 Create OAuth Client ID
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Desktop app** as the application type ⚠️ **Important!**
4. Give it a name like "Volunteer Calendar Integration"
5. Click **Create**
6. Download the JSON file (it will be named something like `client_secret_xxx.json`)
7. Rename the file to `gcp-oauth.keys.json`

## Step 3: Deploy with Calendar Integration

### 3.1 Add OAuth Credentials to Your Project
1. Copy the `gcp-oauth.keys.json` file to your project root directory:
   ```bash
   cp /path/to/downloaded/client_secret_xxx.json ./gcp-oauth.keys.json
   ```

2. Ensure the file has correct permissions:
   ```bash
   chmod 644 ./gcp-oauth.keys.json
   ```

### 3.2 Deploy the Updated System
1. The system is already configured to use Google Calendar MCP in `docker-compose.yaml`
2. Deploy the updated system:
   ```bash
   # If using Coolify, push your changes and redeploy
   git add .
   git commit -m "Add Google Calendar integration"
   git push origin main
   
   # Or if running locally:
   docker-compose up -d --build
   ```

### 3.3 Authenticate the Calendar Service
1. After deployment, you need to authenticate the Google Calendar service:
   ```bash
   # For Coolify deployment, access the container
   docker exec -it <calendar-container-name> npm run auth
   
   # For local deployment
   docker-compose exec google-calendar-mcp npm run auth
   ```

2. The command will display an authentication URL
3. Copy the URL and open it in your browser
4. Sign in with your Google account
5. Grant the requested permissions
6. The authentication will be saved and the service will be ready

## Step 4: Test the Integration

### 4.1 Verify Calendar Service
1. Check that the calendar service is running:
   ```bash
   curl http://localhost:3000/health
   # Should return: {"status":"healthy","server":"google-calendar-mcp","timestamp":"..."}
   ```

### 4.2 Test with the Voice Agent
1. Connect to your LiveKit room
2. Ask the agent: "I need help with cooking in Accra"
3. After the agent finds volunteers, say: "Can you schedule an appointment with Sarah for tomorrow at 2 PM?"
4. The agent should use the calendar tools to create the appointment

## Step 5: Production Considerations

### 5.1 Avoid Weekly Re-authentication (Optional)
If you're tired of re-authenticating every 7 days (test mode limitation):

1. Go to **Google Cloud Console** > **APIs & Services** > **OAuth consent screen**
2. Click **PUBLISH APP** and confirm
3. Your tokens will no longer expire after 7 days
4. ⚠️ Google will show a warning about the app being "unverified" during authentication

### 5.2 Security Best Practices
- Keep your `gcp-oauth.keys.json` file secure and never commit it to version control
- Add `gcp-oauth.keys.json` to your `.gitignore` file
- Use environment variables for sensitive configuration in production
- Regularly review and rotate your OAuth credentials

## Available Calendar Features

Once set up, elderly users can:

### 📅 **Schedule Appointments**
- "Schedule an appointment with Sarah for cooking help tomorrow at 2 PM"
- "Book a companion visit with Michael next Tuesday at 10 AM"

### 📋 **View Appointments**
- "What appointments do I have this week?"
- "Show me my schedule for tomorrow"

### ✏️ **Modify Appointments**
- "Change my appointment with Sarah to 3 PM instead"
- "Cancel my appointment on Friday"

### 🔍 **Check Availability**
- "When am I free this week for a cooking appointment?"
- "Find a good time for a 2-hour companion visit"

## Troubleshooting

### Common Issues

**Authentication URL not working:**
- Make sure you added your email as a test user
- Wait a few minutes for test user propagation
- Try using an incognito browser window

**Calendar service not starting:**
- Check that `gcp-oauth.keys.json` exists and has correct permissions
- Verify the Google Calendar API is enabled
- Check container logs for specific error messages

**Tools not appearing:**
- Verify both MCP servers are running and healthy
- Check the agent logs for MCP connection errors
- Ensure the `GOOGLE_CALENDAR_URL` environment variable is set correctly

### Getting Help

If you encounter issues:
1. Check the container logs: `docker-compose logs google-calendar-mcp`
2. Verify API quotas in Google Cloud Console
3. Ensure your OAuth credentials are correctly configured
4. Test the calendar service health endpoint

## Example Usage Scenarios

### Scenario 1: First-time Scheduling
```
User: "I need help with cooking"
Agent: [Finds volunteers] "I found Sarah Johnson who can help with cooking. Would you like me to schedule an appointment with her?"
User: "Yes, tomorrow at 2 PM"
Agent: [Creates calendar event] "Perfect! I've scheduled a cooking appointment with Sarah Johnson for tomorrow at 2:00 PM at your home. Her phone number is +233-24-123-4567."
```

### Scenario 2: Checking Schedule
```
User: "What do I have scheduled this week?"
Agent: [Lists calendar events] "You have two appointments this week: Cooking help with Sarah on Tuesday at 2 PM, and a companion visit with Michael on Thursday at 10 AM."
```

The Google Calendar integration transforms your volunteer management system into a complete scheduling solution, making it easier for elderly users to not just find volunteers, but actually book and manage appointments with them.