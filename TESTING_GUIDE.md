# Testing Your Volunteer Management Voice Agent

## 🎯 System Status Confirmation

Based on your logs, both services are running successfully:

### ✅ MCP Toolbox Status
```
✓ Initialized 1 sources (SQLite database)
✓ Initialized 7 tools (volunteer search functions)  
✓ Initialized 2 toolsets (elderly_user toolset)
✓ Server ready to serve on port 5001
```

### ✅ LiveKit Agent Status
```
✓ Worker registered with LiveKit Cloud
✓ Connected to: wss://voice-agent-test-0v5cphg4.livekit.cloud
✓ Region: Germany 2
✓ Worker ID: AW_3f5wL3q3aLQE
```

## 🧪 Testing Methods

### Method 1: LiveKit Playground (Recommended)
1. **Access LiveKit Console**: Go to https://cloud.livekit.io/
2. **Navigate to your project**: `voice-agent-test-0v5cphg4`
3. **Go to Playground**: Click "Playground" in the left sidebar
4. **Start a session**: Click "Connect" to join a room
5. **Test voice interaction**: Speak to test the agent

### Method 2: Custom Web Interface
Create a simple HTML test page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Volunteer Agent Test</title>
    <script src="https://unpkg.com/@livekit/components-js@0.12.2/dist/livekit-components.umd.js"></script>
</head>
<body>
    <div id="room-container">
        <livekit-room>
            <livekit-audio-track></livekit-audio-track>
        </livekit-room>
    </div>
    
    <script>
        const room = document.querySelector('livekit-room');
        room.serverUrl = 'wss://voice-agent-test-0v5cphg4.livekit.cloud';
        room.token = 'YOUR_PARTICIPANT_TOKEN'; // Generate from LiveKit Console
    </script>
</body>
</html>
```

### Method 3: Mobile App Testing
Use LiveKit's example apps:
- **iOS**: https://github.com/livekit/client-sdk-swift
- **Android**: https://github.com/livekit/client-sdk-android

## 🗣️ Test Conversations

Try these voice commands to test the volunteer database:

### Basic Volunteer Search
- *"I need help with cooking"*
- *"Find volunteers in Accra"*
- *"I need someone who speaks Twi"*
- *"Find volunteers with transportation"*

### Specific Requests
- *"I need help with medication reminders in Kumasi"*
- *"Find an experienced volunteer for companionship"*
- *"I need someone who can help with grocery shopping"*
- *"Find volunteers who speak English and Ga"*

### Expected Responses
The agent should:
1. **Understand** your request in natural language
2. **Search** the volunteer database using MCP tools
3. **Provide** volunteer details including:
   - Name and contact information
   - Skills and experience
   - Location and availability
   - Languages spoken
   - Transportation options

## 🔍 Debugging & Monitoring

### Check MCP Toolbox Logs
Monitor your Coolify deployment logs for MCP Toolbox to see:
- Database queries being executed
- Tool invocations from the agent
- Any errors or issues

### Check LiveKit Agent Logs
Monitor the agent logs for:
- Voice recognition results
- MCP tool calls
- Response generation
- Any connection issues

### Test Database Directly
You can test the MCP tools directly by making HTTP requests to your MCP Toolbox:

```bash
curl -X POST http://your-coolify-domain:5001/tools/search-volunteers-by-skills \
  -H "Content-Type: application/json" \
  -d '{"skill": "cooking"}'
```

## 🎯 Success Indicators

Your system is working correctly if:

1. **Voice Recognition**: Agent understands your speech
2. **Database Queries**: MCP Toolbox logs show SQL queries
3. **Results Returned**: Agent provides volunteer information
4. **Natural Responses**: Agent speaks in a friendly, elderly-appropriate manner

## 🚨 Troubleshooting

### If Agent Doesn't Respond
- Check LiveKit Console for active connections
- Verify microphone permissions in browser
- Check agent logs for errors

### If No Volunteer Data Returned
- Verify MCP Toolbox is accessible at `http://mcp-toolbox:5000`
- Check database file exists in container
- Test MCP tools directly via HTTP

### If Voice Quality Issues
- Check network connection stability
- Verify audio codec compatibility
- Test with different browsers/devices

## 📱 Production Testing

For production deployment, test with:
- Multiple concurrent users
- Different devices and browsers
- Various network conditions
- Extended conversation sessions

Your volunteer management system is now ready to help elderly users in Ghana find caring volunteers through natural voice interactions!